from flask import Blueprint, jsonify, request
from services.db import get_events

event_info_bp = Blueprint("event_info", __name__, url_prefix="/events")

@event_info_bp.route("/", methods=["GET"])
def get_recent_events():
  try:
    limit = int(request.args.get("limit", 5))
  
    event_type_param = request.args.get("event_type")
    query = {}

    if event_type_param:
      event_types = [et.strip() for et in event_type_param.split(",") if et.strip()]

      if len(event_types) == 1:
        query["event_type"] = event_types[0]
      elif len(event_types) > 1:
        query["event_type"] = {"$in": event_types}

    events = get_events(filter_query=query, limit=limit)

    for e in events:
      e["_id"] = str(e["_id"])
    
    return jsonify(events)
  
  except ValueError:
    return jsonify({"error": "Invalid 'limit' parameter"}), 400
  except Exception as e:
    return jsonify({"error": str(e)}), 500
