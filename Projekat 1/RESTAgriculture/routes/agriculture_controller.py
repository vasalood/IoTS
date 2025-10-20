from quart import Blueprint, jsonify, request
from RESTAgriculture.services.grpc_client import GrpcClient

agriculture_bp = Blueprint('agriculture', __name__)
grpc_client = GrpcClient()

@agriculture_bp.route('/getdata/<int:data_id>', methods=['GET'])
async def get_data(data_id):
	result = await grpc_client.get_data(data_id)
	status_code = result.pop("status_code")
	return jsonify(result), status_code

@agriculture_bp.route("/getdata/timespan", methods=["GET"])
async def get_data_by_timespan():
	start_time = request.args.get("start_time")
	end_time = request.args.get("end_time")
	
	result = await grpc_client.get_data_by_timespan(start_time, end_time)
	status_code = result.pop("status_code")
	return jsonify(result), status_code

@agriculture_bp.route("/updatedata", methods=["PUT"])
def update_data():
	body = request.get_json()
	# expected: { "data_id": 1, "new_location": "New Place" }
	# TODO: pozvati grpc_client.update_data(data_id, new_location)
	pass

@agriculture_bp.route("/adddata", methods=["POST"])
def add_data():
	body = request.get_json()
	# expected: polja iz AddRequest poruke
	# TODO: pozvati grpc_client.add_data(body)
	pass

@agriculture_bp.route("/deletedata/<int:data_id>", methods=["DELETE"])
def delete_data(data_id):
	# TODO: pozvati grpc_client.delete_data(data_id)
	pass

@agriculture_bp.route("/maxtemperature", methods=["GET"])
def max_temperature():
	start_time = request.args.get("start")
	end_time = request.args.get("end")
	# TODO: pozvati grpc_client.max_temperature(start_time, end_time)
	pass

@agriculture_bp.route("/minhumidity", methods=["GET"])
def min_humidity():
	date_time = request.args.get("datetime")
	# TODO: pozvati grpc_client.min_humidity(date_time)
	pass

@agriculture_bp.route("/avgtempandhum", methods=["GET"])
def avg_temp_and_hum():
	body = request.get_json()
	# expected: lista meseci → [{ "year": 2025, "month": 10 }, ...]
	# TODO: pozvati grpc_client.avg_temp_and_hum(body)
	pass

@agriculture_bp.route("/countwaterpumpon", methods=["GET"])
def count_water_pump_on():
	start_time = request.args.get("start")
	end_time = request.args.get("end")
	# TODO: pozvati grpc_client.count_water_pump_on(start_time, end_time)
	pass