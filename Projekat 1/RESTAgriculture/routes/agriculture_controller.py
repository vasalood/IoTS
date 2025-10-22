from datetime import datetime
from quart import Blueprint, jsonify, request
from RESTAgriculture.services.grpc_client import GrpcClient

agriculture_bp = Blueprint('agriculture', __name__)
grpc_client = GrpcClient()

def _get_validated_datetime(param_names: list) -> tuple:
	validated = {}
	for name in param_names:
		value = request.args.get(name)
		if not value:
			return None, jsonify({"error": f"{name} is required"}), 400
		
		try:
			date_time = datetime.fromisoformat(value.replace("Z", "+00:00"))
		except ValueError:
			return None, jsonify({"error": f"{name} must be in ISO format"}), 400
		
		validated[name] = date_time
	
	return validated, None, None

@agriculture_bp.route('/getdata/<data_id>', methods=['GET'])
async def get_data(data_id):
	try:
		data_id = int(data_id)
	except ValueError:
		return jsonify({"error": "data_id must be an integer"}), 400
	
	if data_id <= 0:
		return jsonify({"error": "data_id must be a positive integer"}), 400
	
	result = await grpc_client.get_data(data_id)
	status_code = result.pop("status_code")
	return jsonify(result), status_code

@agriculture_bp.route("/getdata/timespan", methods=["GET"])
async def get_data_by_timespan():
	validated, error_response, status_code = _get_validated_datetime(["start_time", "end_time"])
	
	if error_response:
		return error_response, status_code

	start_time = validated["start_time"]
	end_time = validated["end_time"]
	
	result = await grpc_client.get_data_by_timespan(start_time, end_time)
	status_code = result.pop("status_code")

	return jsonify(result), status_code

@agriculture_bp.route("/updatedata", methods=["PATCH"])
async def update_data():
	body = await request.get_json()

	required_fields = ["data_id", "new_location"]
	missing_fields = [field for field in required_fields if field not in body]

	if missing_fields:
		return jsonify({
			"error": f"Missing required fields: {', '.join(missing_fields)}"
		}), 400

	try:
		data_id = int(body["data_id"])
		new_location = str(body["new_location"]).strip()

		if not new_location:
			return jsonify({"error": "New location cannot be empty"}), 400

	except (ValueError, TypeError, KeyError) as e:
		return jsonify({"error": f"Invalid data: {e}"}), 400

	result = await grpc_client.update_data(data_id, new_location)
	status_code = result.pop("status_code")

	return jsonify(result), status_code

@agriculture_bp.route("/add-data", methods=["POST"])
async def add_data():
	body = await request.get_json()

	required_fields = [
		"location", "sensor_name", "temperature",
		"humidity", "water_level", "K", "P", "N",
		"watering_plant_pump_ON"
	]
	
	missing_fields = [field for field in required_fields if field not in body]
	if missing_fields:
		return jsonify({
			"error": f"Missing required fields: {', '.join(missing_fields)}"
		}), 400

	try:
		body["temperature"] = int(body["temperature"])
		body["humidity"] = int(body["humidity"])
		body["water_level"] = int(body["water_level"])
		body["K"] = int(body["K"])
		body["P"] = int(body["P"])
		body["N"] = int(body["N"])
		body["watering_plant_pump_ON"] = bool(body["watering_plant_pump_ON"])
		body["location"] = str(body["location"]).strip()
		body["sensor_name"] = str(body["sensor_name"]).strip()

		if not body["location"] or not body["sensor_name"]:
			raise ValueError("Empty string for location or sensor_name")
		
	except (ValueError, TypeError, KeyError) as e:
		return jsonify({"error": f"Invalid data: {e}"}), 400

	result = await grpc_client.add_data(body)
	status_code = result.pop("status_code")

	return jsonify(result), status_code

@agriculture_bp.route("/deletedata/<data_id>", methods=["DELETE"])
async def delete_data(data_id):
	try:
		data_id = int(data_id)
	except ValueError:
		return jsonify({"error": "data_id must be an integer"}), 400
	
	if data_id <= 0:
		return jsonify({"error": "data_id must be a positive integer"}), 400
	
	result = await grpc_client.delete_data(data_id)
	status_code = result.pop("status_code")
	return jsonify(result), status_code

@agriculture_bp.route("/maxtemperature", methods=["GET"])
async def max_temperature():
	validated, error_response, status_code = _get_validated_datetime(["start_time", "end_time"])
	
	if error_response:
		return error_response, status_code
	
	start_time = validated["start_time"]
	end_time = validated["end_time"]
	
	result = await grpc_client.max_temperature(start_time, end_time)
	status_code = result.pop("status_code")

	return jsonify(result), status_code

@agriculture_bp.route("/minhumidity", methods=["GET"])
async def min_humidity():
	validated, error_response, status_code = _get_validated_datetime(["date_time"])
	if error_response:
		return error_response, status_code
	
	date_time = validated["date_time"]

	result = await grpc_client.min_humidity(date_time)
	status_code = result.pop("status_code")

	return jsonify(result), status_code

@agriculture_bp.route("/avgtempandhum", methods=["POST"])
async def avg_temp_and_hum():
	body = await request.get_json()

	if not isinstance(body, list):
		return jsonify({"error": "Request body must be a list of months"}), 400

	valid_months = []
	for data in body:
		if "year" not in data or "month" not in data:
				continue
		if not isinstance(data["year"], int) or not isinstance(data["month"], int):
				continue
		valid_months.append({"year": data["year"], "month": data["month"]})

	if not valid_months:
		return jsonify({"error": "No valid months provided"}), 400

	results = await grpc_client.avg_temp_and_hum(valid_months)
	return jsonify({"results": results}), 200

@agriculture_bp.route("/countwaterpumpon", methods=["GET"])
async def count_water_pump_on():
	validated, error_response, status_code = _get_validated_datetime(["start_time", "end_time"])
	
	if error_response:
		return error_response, status_code
	
	start_time = validated["start_time"]
	end_time = validated["end_time"]
	
	result = await grpc_client.count_water_pump_on(start_time, end_time)
	status_code = result.pop("status_code")
	
	return jsonify(result), status_code