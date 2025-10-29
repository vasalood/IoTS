import json, socket
import paho.mqtt.client as mqtt
from mqtt_client.handler import handle_sensor_data

BROKER_HOST = "mosquitto"
BROKER_PORT = 1883
SENSOR_TOPIC = "sensors/data"
EVENT_TOPIC = "analytics/events"

def on_connect(client, userdata, flags, rc):
  if rc == 0:
    print("Connected to MQTT broker.", flush=True)
    client.subscribe(SENSOR_TOPIC)
    print(f"Subscribed to topic: {SENSOR_TOPIC}", flush=True)
  else:
    print(f"Failed to connect, return code {rc}", flush=True)

def on_message(client, userdata, msg):
  try:
    payload = json.loads(msg.payload.decode())
    print(f"Received message on {msg.topic}")

    events = handle_sensor_data(payload)
    print(f"Detected {len(events)} events.", flush=True)

    for event in events:
      event_json = json.dumps(event)
      client.publish(EVENT_TOPIC, event_json)
      #print(f"Published event to {EVENT_TOPIC}: {event_json}")

  except Exception as e:
    print(f"Error processing message: {e}", flush=True)

def on_disconnect(client, userdata, rc):
  print(f"Disconnected from MQTT broker with code {rc}.", flush=True)

def start_mqtt_client():
  client = mqtt.Client(client_id="analytics-service")

  client.on_connect = on_connect
  client.on_message = on_message
  client.on_disconnect = on_disconnect

  try:
    client.connect(BROKER_HOST, BROKER_PORT, keepalive=60)
    print(f"Connecting to broker at {BROKER_HOST}:{BROKER_PORT} ...", flush=True)
  except socket.error as e:
    print(f"Failed to connect to broker: {e}", flush=True)


  client.loop_start()
  
  return client


