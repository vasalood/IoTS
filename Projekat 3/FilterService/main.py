import time
from mqtt_client.client import start_filter_service

BROKER_HOST = "mosquitto"
BROKER_PORT = 1883
BROKER_TOPIC = "sensor/data"

NATS_URL = "nats://nats-server:4222"
NATS_SUBJECT = "avg.sensor.data"

WINDOW_SEC = "15"

if __name__ == "__main__":
  print("Starting FilterService...", flush=True)

  stop_fn = start_filter_service(
    mqtt_host=BROKER_HOST,
    mqtt_port=BROKER_PORT,
    mqtt_topic=BROKER_TOPIC,
    nats_url=NATS_URL,
    nats_subject=NATS_SUBJECT,
    window_sec=WINDOW_SEC,
  )

  try:
    while True:
      time.sleep(1)
  except KeyboardInterrupt:
    print("Stopping FilterService...", flush=True)
    stop_fn()
    print("FilterService stopped.", flush=True)