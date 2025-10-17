import grpc
from RESTAgriculture.services.GeneratedProtoClient import greet_pb2, greet_pb2_grpc

class GrpcClient:
    def __init__(self, host="localhost", port=5250):
        self.channel = grpc.insecure_channel(f"{host}:{port}")
        self.stub = greet_pb2_grpc.GreeterStub(self.channel)

    def get_sensor_data(self, data_id: int):
        request = greet_pb2.SensorRequest(data_id=data_id)
        try:
            response = self.stub.GetSensorData(request)
            # Vraća dictionary da Flask može lako da jsonify
            return {
                "data_id": response.data_id,
                "temperature": response.temperature,
                "humidity": response.humidity,
                "water_level": response.water_level,
                "timestamp": response.timestamp
            }
        except grpc.RpcError as e:
            return {"error": e.details(), "code": e.code().name}