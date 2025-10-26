from flask import Flask, jsonify
from services.mqtt_client import run_in_background
from routes.event_info_controller import event_info_bp

app = Flask(__name__)

run_in_background()

app.register_blueprint(event_info_bp)

@app.route("/status", methods=["GET"])
def status():
  return jsonify({"status": "EventInfoService radi!"})

if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000)
