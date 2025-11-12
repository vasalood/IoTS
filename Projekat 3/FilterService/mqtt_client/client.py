import json
import socket
import threading
import paho.mqtt.client as mqtt

class MqttWorker:
  def __init__(self, host, port, topic, on_measure): 
    """
    host/port/topic: parametri za MQTT broker i topic
    on_measure: funkcija (dict) -> None, koju zovemo kad stigne JSON poruka
    """
    self.host = host
    self.port = port
    self.topic = topic
    self.on_measure = on_measure

    # napravimo Paho klijenta
    self.client = mqtt.Client(client_id="filter-service")
    self.client.on_connect = self._on_connect
    self.client.on_message = self._on_message
    self.client.on_disconnect = self._on_disconnect

    self._started = False
    self._lock = threading.Lock()

  # === MQTT callbacks ===
  def _on_connect(self, client, userdata, flags, rc):
    if rc == 0:
      print(f"[mqtt] Connected to {self.host}:{self.port}", flush=True)
      client.subscribe(self.topic)
      print(f"[mqtt] Subscribed to {self.topic}", flush=True)
    else:
      print(f"[mqtt] Connect failed, rc={rc}", flush=True)

  def _on_message(self, client, userdata, msg):
    try:
      payload = json.loads(msg.payload.decode("utf-8"))
      # delegiramo FilterService-u
      self.on_measure(payload)

      print(f"Payload from {self.topic} is {payload}")
    except Exception as e:
      print(f"[mqtt] Bad message ({e}). Topic={msg.topic}", flush=True)

  def _on_disconnect(self, client, userdata, rc):
    print(f"[mqtt] Disconnected, rc={rc}", flush=True)

  # === lifecycle ===
  def start(self):
    with self._lock:
      if self._started:
        return
      try:
        print(f"[mqtt] Connecting to {self.host}:{self.port} ...", flush=True)
        self.client.connect(self.host, self.port, keepalive=60)
      except socket.error as e:
        print(f"[mqtt] Connect error: {e}", flush=True)
        # i dalje pokušavamo loop_start; Paho će re-try
      self.client.loop_start()  # nit u pozadini
      self._started = True

  def stop(self):
    with self._lock:
      if not self._started:
        return
      print("[mqtt] Stopping loop...", flush=True)
      self.client.disconnect()
      self.client.loop_stop()
      self._started = False