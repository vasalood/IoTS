import os

MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb://mongoadmin:Vasamare123@mongo-project-2:27017/"
)
MONGO_DB = os.getenv("MONGO_DB", "agriculture_database")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "iot_events_timeseries")

BROKER_HOST = os.getenv("MQTT_HOST", "mosquitto")
BROKER_PORT = int(os.getenv("MQTT_PORT", 1883))
BROKER_TOPIC = os.getenv("MQTT_TOPIC", "analytics/events")