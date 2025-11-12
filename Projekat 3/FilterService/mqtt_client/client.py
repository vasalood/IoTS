import json
import time
import threading
from collections import defaultdict

import paho.mqtt.client as mqtt

import asyncio
import nats


class NatsPublisher:
  """
  Jednostavan NATS publisher koji radi u POSEBNOJ NITI sa svojim asyncio event loop-om.
  - start(url): pokreće nit, kreira loop, connect-uje NATS i čuva nc konekciju
  - publish(subject, dict_payload): thread-safe publish
  - stop(): graciozno zatvara nc i gasi loop/nit
  """
  def __init__(self, url: str):
    self.url = url
    self.loop = None
    self.nc = None
    self._thread = None

  def start(self):
    def runner():
      self.loop = asyncio.new_event_loop()
      asyncio.set_event_loop(self.loop)
      self.loop.run_until_complete(self._connect())
      self.loop.run_forever()

    self._thread = threading.Thread(target=runner, daemon=True)
    self._thread.start()

    # sačekamo da se konekcija uspostavi
    while self.loop is None or self.nc is None:
      time.sleep(0.05)

  async def _connect(self):
    self.nc = await nats.connect(servers=[self.url])

  def publish(self, subject: str, payload: dict):
    if not self.loop or not self.nc:
      return
    async def _pub():
      await self.nc.publish(subject, json.dumps(payload).encode("utf-8"))
    asyncio.run_coroutine_threadsafe(_pub(), self.loop)

  def stop(self):
    if not self.loop:
      return
    async def _drain_and_stop():
      try:
        if self.nc:
          await self.nc.drain()
      finally:
        self.loop.stop()
    fut = asyncio.run_coroutine_threadsafe(_drain_and_stop(), self.loop)
    try:
      fut.result(timeout=3)
    except Exception:
      pass
    if self._thread and self._thread.is_alive():
      self._thread.join(timeout=3)


class FilterService:
  """
  Filter servis:
  - subscribe na MQTT `mqtt_topic`
  - skuplja merenja u "tumbling" prozoru od window_sec
  - kad prozor istekne: izračuna prosek i pošalje na NATS `nats_subject`
  """
  def __init__(self, mqtt_host, mqtt_port, mqtt_topic, nats_url, nats_subject, window_sec):
    self.mqtt_host = mqtt_host
    self.mqtt_port = mqtt_port
    self.mqtt_topic = mqtt_topic
    self.nats_subject = nats_subject
    self.window_sec = window_sec

    # paho MQTT klijent
    self._mqtt = mqtt.Client(client_id="filter-service")
    self._mqtt.on_connect = self._on_connect
    self._mqtt.on_message = self._on_message
    self._mqtt.on_disconnect = self._on_disconnect

    # NATS publisher (posebna nit)
    self._nats = NatsPublisher(nats_url)

    # Bufferi po "device_id" (ako nema, sve ide u "unknown")
    # Svaki entry: {"ws": window_start_epoch, "items": [float_temp, ...]}
    self._buckets = defaultdict(lambda: {"ws": None, "items": []})

    # Za graciozno gašenje
    self._stop_event = threading.Event()

    # Ticker nit (svake 1s proveri da li je neki prozor "preležao" i treba flush)
    self._ticker_thread = threading.Thread(target=self._ticker, daemon=True)

  # ---------- MQTT callbacks ----------
  def _on_connect(self, client, userdata, flags, rc):
    if rc == 0:
      print(f"[MQTT] Connected to {self.mqtt_host}:{self.mqtt_port}", flush=True)
      client.subscribe(self.mqtt_topic)
      print(f"[MQTT] Subscribed: {self.mqtt_topic}", flush=True)
    else:
      print(f"[MQTT] Failed to connect, rc={rc}", flush=True)

  def _on_disconnect(self, client, userdata, rc):
    print(f"[MQTT] Disconnected (rc={rc})", flush=True)

  def _on_message(self, client, userdata, msg):
    try:
      payload = json.loads(msg.payload.decode("utf-8"))
      # očekujemo npr: {"sensor_name":"MKR1010_WIFI","temperature":23.1}
      temperature = payload.get("temperature")
      device_id = payload.get("sensor_name")
      if temperature is None:
        return

      now = int(time.time())
      ws = now - (now % self.window_sec)  # tumbling window start

      b = self._buckets[device_id]
      # ako je prvi put
      if b["ws"] is None:
        b["ws"] = ws

      # ako se promenio prozor, prvo flush starog
      if b["ws"] != ws and b["items"]:
        self._flush(device_id)

      # dodaj trenutnu merenje u aktivni prozor
      b["ws"] = ws
      b["items"].append(float(temperature))

    except Exception as e:
      print(f"[Filter] Error on_message: {e}", flush=True)

  # ---------- Window flush ----------
  def _flush(self, device_id: str):
    b = self._buckets[device_id]
    if not b["items"]:
      return
    temps = b["items"]
    avg_temp = sum(temps) / len(temps)

    t_start = b["ws"]
    t_end = b["ws"] + self.window_sec

    out = {
      "device_id": device_id,
      "window": {"type": "tumbling", "size_sec": self.window_sec},
      "t_start": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t_start)),
      "t_end":   time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t_end)),
      "avg": {"temperature": avg_temp},
      "count": len(temps)
    }

    # Publish na NATS u posebnoj niti/loopu
    self._nats.publish(self.nats_subject, out)
    # resetuj bucket
    b["items"].clear()

  # ---------- Periodički "ticker": ako dugo nije stigla poruka, ipak pošalji prozor ----------
  def _ticker(self):
    while not self._stop_event.is_set():
      time.sleep(1)
      now = int(time.time())
      for device_id, b in list(self._buckets.items()):
        if b["ws"] is None or not b["items"]:
          continue
        # ako je trenutni epoch prešao granicu prozora b["ws"] + window_sec
        if now >= b["ws"] + self.window_sec:
          self._flush(device_id)
          # obično se novi ws postavlja na _on_message,
          # ovde samo pazimo da se ne izgube zakasneli uzorci

  # ---------- Lifecycle ----------
  def start(self):
    # 1) NATS publisher
    self._nats.start()
    # 2) MQTT konekcija + loop u pozadini
    self._mqtt.connect(self.mqtt_host, self.mqtt_port, keepalive=60)
    self._mqtt.loop_start()
    # 3) Start ticker niti
    self._ticker_thread.start()

  def stop(self):
    # zaustavi ticker
    self._stop_event.set()
    if self._ticker_thread.is_alive():
      self._ticker_thread.join(timeout=2)

    # MQTT loop stop + disconnect
    try:
      self._mqtt.loop_stop()
      self._mqtt.disconnect()
    except Exception:
      pass

    # NATS zatvaranje
    try:
      self._nats.stop()
    except Exception:
      pass


def start_filter_service(mqtt_host, mqtt_port, mqtt_topic, nats_url, nats_subject, window_sec):
  """
  Fabrika: startuje servis i vraća funkciju zaustavljanja (stop_fn).
  To omogućava da main.py DRŽI proces upaljenim i graciozno ga ugasi na Ctrl+C.
  """
  svc = FilterService(
    mqtt_host=mqtt_host,
    mqtt_port=mqtt_port,
    mqtt_topic=mqtt_topic,
    nats_url=nats_url,
    nats_subject=nats_subject,
    window_sec=window_sec,
  )
  svc.start()

  def stop_fn():
    svc.stop()

  return stop_fn
