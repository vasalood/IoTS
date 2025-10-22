import grpc
from datetime import datetime
from google.protobuf.timestamp_pb2 import Timestamp
from services.GeneratedProtoClient import agriculture_pb2, agriculture_pb2_grpc

class GrpcClient:
  def __init__(self, host="localhost", port=5250):
    self.host = host
    self.port = port
    self.stub = None

  def _convert_to_timestamp(self, date: datetime) -> Timestamp:
    timestamp = Timestamp()
    timestamp.FromDatetime(date)
    return timestamp
  
  def _handle_grpc_error(self, e: grpc.RpcError) -> dict:
    message = e.details() or "Internal server error"

    if e.code() == grpc.StatusCode.INVALID_ARGUMENT: 
      return {"error": message, "status_code": 400} 
    elif e.code() == grpc.StatusCode.NOT_FOUND: 
      return {"error": message, "status_code": 404} 
    else: 
      return {"error": message, "status_code": 500}
  
  def _format_single_data_response(self, response) -> dict:
    return {
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
    }

  async def _get_stub(self):
    if self.stub is None:
      self.channel = grpc.aio.insecure_channel(f"{self.host}:{self.port}")
      self.stub = agriculture_pb2_grpc.AgricultureStub(self.channel)
    return self.stub

  async def get_data(self, data_id: int):
    stub = await self._get_stub()
    try:
        request = agriculture_pb2.RequestById(data_id=data_id)
        response = await stub.GetData(request)
        data = self._format_single_data_response(response)
        return {
          "data": data, 
          "status_code": 200
        }
    
    except grpc.RpcError as e:
      return self._handle_grpc_error(e)

  async def get_data_by_timespan(self, start_time: datetime, end_time: datetime):
    stub = await self._get_stub()
    try:
      start_timestamp = self._convert_to_timestamp(start_time)
      end_timestamp = self._convert_to_timestamp(end_time)

      request = agriculture_pb2.RequestByTimeSpan(
        start_time=start_timestamp,
        end_time=end_timestamp
      )

      response_stream = stub.GetDataByTimeSpan(request)

      results = []
      async for response in response_stream:
        results.append(self._format_single_data_response(response))

      return {
        "data": results, 
        "status_code": 200
      }

    except grpc.RpcError as e:
      return self._handle_grpc_error(e)

  async def update_data(self, data_id: int, new_location: str):
    stub = await self._get_stub()
    
    request = agriculture_pb2.UpdateRequest(
      data_id=data_id,
      new_location=new_location
    )

    try:
      response = await stub.UpdateData(request)
      return {
        "message": response.feedback,
        "status_code": 200
      }
    except grpc.RpcError as e:
      return self._handle_grpc_error(e)

  async def add_data(self, data: dict):
    stub = await self._get_stub()

    request = agriculture_pb2.AddRequest(
      location=data["location"],
      sensor_name=data["sensor_name"],
      temperature=data["temperature"],
      humidity=data["humidity"],
      water_level=data["water_level"],
      K=data["K"],
      P=data["P"],
      N=data["N"],
      watering_plant_pump_ON=data["watering_plant_pump_ON"]
    )

    try:
      response = await stub.AddData(request)
      return {
        "message": response.feedback, 
        "status_code": 200
      }
    except grpc.RpcError as e:
      return self._handle_grpc_error(e)

  async def delete_data(self, data_id: int):
    stub = await self._get_stub()
    try:
      request = agriculture_pb2.RequestById(data_id=data_id)
      response = await stub.DeleteData(request)

      return {
        "message": response.feedback, 
        "status_code": 200
      }

    except grpc.RpcError as e:
      return self._handle_grpc_error(e)

  async def max_temperature(self, start_time: datetime, end_time: datetime):
    stub = await self._get_stub()
    try:
      start_timestamp = self._convert_to_timestamp(start_time)
      end_timestamp = self._convert_to_timestamp(end_time)

      request = agriculture_pb2.RequestByTimeSpan(
        start_time=start_timestamp,
        end_time=end_timestamp
      )

      response = await stub.MaxTemperature(request)
      data = self._format_single_data_response(response)

      return {
        "data": data,
        "status_code": 200
      }
    
    except grpc.RpcError as e:
      return self._handle_grpc_error(e)

  async def min_humidity(self, date_time: datetime):
    stub = await self._get_stub()
    try:
      timestamp = self._convert_to_timestamp(date_time)

      request = agriculture_pb2.RequestByStartDateTime(date_time=timestamp)
      response = await stub.MinHumidity(request)
      data = self._format_single_data_response(response)

      return {
        "data": data,
        "status_code": 200
      }
    except grpc.RpcError as e:
      return self._handle_grpc_error(e)

  async def avg_temp_and_hum(self, months: list):
    stub = await self._get_stub()

    async def request_generator():
      for data in months:
        yield agriculture_pb2.MonthRequest(year=data["year"], month=data["month"])

    results = []
    try:
      async for response in stub.AvgTempAndHum(request_generator()):
        if response.isValid:
          results.append({
            "month_label": response.month_label,
            "temperature": response.temperature,
            "humidity": response.humidity
          })
        else:
          results.append({
            "month_label": response.month_label,
            "error_message": response.error_message
          })
        
      return {"data": results, "status_code": 200}

    except grpc.RpcError as e:
      return self._handle_grpc_error(e)

  async def count_water_pump_on(self, start_time: datetime, end_time: datetime):
    stub = await self._get_stub()
    try:
      start_timestamp = self._convert_to_timestamp(start_time)
      end_timestamp = self._convert_to_timestamp(end_time)

      request = agriculture_pb2.RequestByTimeSpan(
          start_time=start_timestamp,
          end_time=end_timestamp
      )

      response = await stub.CountWaterPumpOn(request)

      return {
        "count": response.count, 
        "status_code": 200
      }

    except grpc.RpcError as e:
      return self._handle_grpc_error(e)