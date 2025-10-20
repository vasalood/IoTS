import grpc
from datetime import datetime
from google.protobuf.timestamp_pb2 import Timestamp
from RESTAgriculture.services.GeneratedProtoClient import agriculture_pb2, agriculture_pb2_grpc

class GrpcClient:
  def __init__(self, host="localhost", port=5250):
    self.host = host
    self.port = port
    self.stub = None
    
  async def _get_stub(self):
    if self.stub is None:
      self.channel = grpc.aio.insecure_channel(f"{self.host}:{self.port}")
      self.stub = agriculture_pb2_grpc.AgricultureStub(self.channel)
    return self.stub

  async def get_data(self, data_id: int):
    stub = await self._get_stub()
    request = agriculture_pb2.RequestById(data_id=data_id)
    try:
        response = await stub.GetData(request)
        
        return {
            "data": {
              "data_id": response.metadata.data_id,
              "location": response.metadata.location,
              "sensor_name": response.metadata.sensor_name,
              "temperature": response.temperature,
              "humidity": response.humidity,
              "water_level": response.water_level,
              "K": response.K,
              "P": response.P,
              "N": response.N,
              "timestamp": response.timestamp
            },
            "status_code": 200
        }
    except grpc.RpcError as e:
        message = e.details() or "Internal server error"
        if e.code() == grpc.StatusCode.NOT_FOUND:
          return {"message": message, "status_code": 404}
        else:
          return {"message": message, "status_code": 500}

  async def get_data_by_timespan(self, start_time: str, end_time: str):
    stub = await self._get_stub()
    try:
      start_datetime = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
      end_datetime = datetime.fromisoformat(end_time.replace("Z", "+00:00"))

      start_timestamp = Timestamp()
      end_timestamp = Timestamp()
      start_timestamp.FromDatetime(start_datetime)
      end_timestamp.FromDatetime(end_datetime)

      request = agriculture_pb2.RequestByTimeSpan(
        start_time=start_timestamp,
        end_time=end_timestamp
      )

      response_stream = stub.GetDataByTimeSpan(request)

      results = []
      async for response in response_stream:
        results.append({
          "data_id": response.metadata.data_id,
          "location": response.metadata.location,
          "sensor_name": response.metadata.sensor_name,
          "temperature": response.temperature,
          "humidity": response.humidity,
          "water_level": response.water_level,
          "K": response.K,
          "P": response.P,
          "N": response.N,
          "watering_plant_pump_ON": response.watering_plant_pump_ON,
          "timestamp": response.timestamp
        })

      return {"data": results, "status_code": 200}

    except grpc.RpcError as e:
      message = e.details() or "Internal server error"

      if e.code() == grpc.StatusCode.INVALID_ARGUMENT:
          return {"message": message, "status_code": 400}
      elif e.code() == grpc.StatusCode.NOT_FOUND:
          return {"message": message, "status_code": 404}
      else:
          return {"message": message, "status_code": 500}

  async def update_data(self, data_id: int, new_location: str):
    stub = await self._get_stub()
    ...

  async def add_data(self, data: dict):
    stub = await self._get_stub()
    ...

  async def delete_data(self, data_id: int):
    stub = await self._get_stub()
    ...

  async def max_temperature(self, start_time: str, end_time: str):
    stub = await self._get_stub()
    ...

  async def min_humidity(self, date_time: str):
    stub = await self._get_stub()
    ...

  async def avg_temp_and_hum(self, months: list):
    stub = await self._get_stub()
    ...

  async def count_water_pump_on(self, start_time: str, end_time: str):
    stub = await self._get_stub()
    ...