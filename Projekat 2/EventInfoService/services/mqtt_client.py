import json
import threading
import paho.mqtt.client as mqtt
from datetime import datetime
from services.db import insert_event
from utils.config import BROKER_HOST, BROKER_PORT, BROKER_TOPIC

def process_event(payload: dict):
  try:
    ts = datetime.fromisoformat(payload["timestamp"].replace("Z", "+00:00"))
    doc = {
      "timestamp": ts,
      "metadata": {
        "data_id": payload["data_id"],
        "sensor_name": payload["sensor_name"],
        "location": payload["location"]
      },
      "event_type": payload["event_type"],
      "value": payload["value"]
    }

    if "threshold" in payload:
      doc["threshold"] = payload["threshold"]

    insert_event(doc)
  except Exception as e:
    print("Error processing event:", e)


def on_connect(client, userdata, flags, rc):
    if rc == 0:
      print("Connected to MQTT broker.")
      client.subscribe(BROKER_TOPIC)
      print(f"Subscribed to topic: {BROKER_TOPIC}")
    else:
      print(f"[MQTT Client] Connection failed with code {rc}")

def on_message(client, userdata, msg):
  try:
    payload = json.loads(msg.payload.decode())
    print(f"Received message on {msg.topic}")
    
    process_event(payload)

  except Exception as e:
    print("Error on message:", e)

def on_disconnect(client, userdata, rc):
  print(f"Disconnected from MQTT broker with code {rc}.")

def start_mqtt_client():
  client = mqtt.Client(client_id="event-info-service")
  client.on_connect = on_connect
  client.on_message = on_message
  client.on_disconnect = on_disconnect

  client.connect(BROKER_HOST, BROKER_PORT, keepalive=60)
  client.loop_start()

def run_in_background():
  thread = threading.Thread(target=start_mqtt_client)
  thread.daemon = True
  thread.start()
  print("MQTT client running in a background thread")
