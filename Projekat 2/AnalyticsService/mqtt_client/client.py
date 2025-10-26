import json
import paho.mqtt.client as mqtt
from mqtt_client.handler import handle_sensor_data

BROKER_HOST = "localhost"
BROKER_PORT = 1883
SENSOR_TOPIC = "sensors/data"
EVENT_TOPIC = "analytics/events"

def on_connect(client, userdata, flags, rc):
  if rc == 0:
    print("Connected to MQTT broker.")
    client.subscribe(SENSOR_TOPIC)
    print(f"Subscribed to topic: {SENSOR_TOPIC}")
  else:
    print(f"Failed to connect, return code {rc}")

def on_message(client, userdata, msg):
  try:
    payload = json.loads(msg.payload.decode())
    print(f"Received message on {msg.topic}")

    events = handle_sensor_data(payload)
    print(f"Detected {len(events)} events.")

    for event in events:
      event_json = json.dumps(event)
      client.publish(EVENT_TOPIC, event_json)
      #print(f"Published event to {EVENT_TOPIC}: {event_json}")

  except Exception as e:
    print(f"Error processing message: {e}")

def on_disconnect(client, userdata, rc):
  print(f"Disconnected from MQTT broker with code {rc}.")

def start_mqtt_client():
  client = mqtt.Client(client_id="analytics-service")

  client.on_connect = on_connect
  client.on_message = on_message
  client.on_disconnect = on_disconnect

  client.connect(BROKER_HOST, BROKER_PORT, keepalive=60)
  client.loop_start()
  
  return client