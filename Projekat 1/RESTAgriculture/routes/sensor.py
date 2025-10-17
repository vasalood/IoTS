from flask import Blueprint, jsonify
from RESTAgriculture.services.grpc_client import GrpcClient

sensor_bp = Blueprint('sensor', __name__)
grpc_client = GrpcClient()  # koristi default host i port

@sensor_bp.route('/sensors/<int:data_id>', methods=['GET'])
def get_sensor(data_id):
    result = grpc_client.get_sensor_data(data_id)
    return jsonify(result)