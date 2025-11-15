import sys
import time
import signal

from nats_client.publisher import NatsPublisher
from services.filter import FilterService
from mqtt_client.client import MqttWorker

BROKER_HOST = "mosquitto"
BROKER_PORT = 1883
BROKER_TOPIC = "sensor/data"

NATS_URL = "nats://nats-server:4222"
NATS_SUBJECT = "avg.sensor.data"

WINDOW_SEC = 15

def main():
  print("[main] Starting FilterService stack...", flush=True)

  # 1) NATS publisher (pozadinski asyncio loop u posebnoj niti)
  nats_pub = NatsPublisher(servers=NATS_URL)
  nats_pub.start()  # podiže nit i konektuje se na NATS

  # 2) FilterService (računa prosek na tumbling prozoru)
  filter_service = FilterService(
    window_sec=WINDOW_SEC,
    subject_prefix=NATS_SUBJECT,
    nats_publisher=nats_pub
  )

  # 3) MQTT radnik (pretplata na sensor/data i prosleđivanje ka FilterService)
  mqtt = MqttWorker(
    host=BROKER_HOST,
    port=BROKER_PORT,
    topic=BROKER_TOPIC,
    on_measure=filter_service.ingest  # CALLBACK za svaki primljeni JSON
  )
  mqtt.start()

  # 4) graceful shutdown: definišemo stop_fn i signal handlere
  def stop_fn(signum=None, frame=None):
    print("\n[main] Stopping gracefully ...", flush=True)
    mqtt.stop()         # zaustavi paho.loop
    filter_service.stop()  # opcionalno (ako nešto čisti)
    nats_pub.stop()     # zaustavi asyncio loop nit i zatvori NATS
    print("[main] Stopped. Bye.", flush=True)
    sys.exit(0)

  signal.signal(signal.SIGINT, stop_fn)   # Ctrl+C
  signal.signal(signal.SIGTERM, stop_fn)  # docker stop

  # 5) Držimo proces živ dok ne stigne signal
  try:
    while True:
      time.sleep(1)
  except KeyboardInterrupt:
    stop_fn()

if __name__ == "__main__":
  main()