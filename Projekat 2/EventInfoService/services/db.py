from pymongo import MongoClient
from utils.config import MONGO_URI, MONGO_DB, MONGO_COLLECTION

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
collection = db[MONGO_COLLECTION]

def insert_event(event_data):
  try:
    collection.insert_one(event_data)
    print(f"[MongoDB] Event inserted: {event_data}")
  except Exception as e:
    print(f"[MongoDB] Error inserting event: {e}")

def get_events(filter_query=None, limit=5):
  query = filter_query or {}
  try:
    events = list(
      collection.find(query).sort("timestamp", -1).limit(limit)
    )
    return events
  except Exception as e:
    print(f"[MongoDB] Error retrieving events: {e}")
    return []