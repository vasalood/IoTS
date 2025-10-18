using DnsClient.Protocol;
using Grpc.Core;
using GrpcAgriculture.Models;
using Microsoft.AspNetCore.Components.Routing;
using MongoDB.Driver;

namespace GrpcAgriculture.Services;

public class AgricultureService : Agriculture.AgricultureBase
{
  private readonly DatabaseService _mongo;
  public AgricultureService(DatabaseService mongo)
    {
        _mongo = mongo;
    }
  public override async Task<SingleDataResponse> GetData(RequestById request, ServerCallContext context)
  {
    try
    {
      var collection = _mongo.GetCollection<DataModel>("iot_data_timeseries");

      var filter = Builders<DataModel>.Filter.And(
        Builders<DataModel>.Filter.Eq(x => x.Metadata!.DataId, request.DataId),
        Builders<DataModel>.Filter.Eq(x => x.Metadata!.IsDataDeleted, false)
      );

      var data = await collection.Find(filter).FirstOrDefaultAsync();

      if (data == null)
        throw new RpcException(new Status(StatusCode.NotFound, "Data not found, check the data_id!"));

      return await Task.FromResult(new SingleDataResponse
      {
        Response = new Data
        {
          Metadata = new Metadata
          {
            DataId = data.Metadata!.DataId,
            Location = data.Metadata!.Location,
            SensorName = data.Metadata!.SensorName
          },
          Temperature = data.Temperature,
          Humidity = data.Humidity,
          WaterLevel = data.WaterLevel,
          K = data.K,
          P = data.P,
          N = data.N,
          WateringPlantPumpON = data.WateringPumpOn,
        },
        Timestamp = data.Timestamp.ToString("O")
      });
    }
    catch (RpcException)
    {
      throw;
    }
    catch (Exception ex)
    {
      throw new RpcException(new Status(StatusCode.Internal, $"Server error: {ex.Message}"));
    }
  }
  public override async Task GetDataByTimeSpan(RequestByTimeSpan request, IServerStreamWriter<SingleDataResponse> responseStream, ServerCallContext context)
  {
    try
    {
      if (request.StartTime == null || request.EndTime == null)
        throw new RpcException(new Status(StatusCode.InvalidArgument, "StartTime and EndTime must be provided."));

      var collection = _mongo.GetCollection<DataModel>("iot_data_timeseries");

      var startTime = request.StartTime.ToDateTime();
      var endTime = request.EndTime.ToDateTime();

      if (startTime > endTime)
      {
        (startTime, endTime) = (endTime, startTime);
      }

      var filter = Builders<DataModel>.Filter.And(
        Builders<DataModel>.Filter.Gte(x => x.Timestamp, startTime),
        Builders<DataModel>.Filter.Lte(x => x.Timestamp, endTime),
        Builders<DataModel>.Filter.Eq(x => x.Metadata!.IsDataDeleted, false)
      );

      var data = await collection.FindAsync(filter);

      await foreach (var res in data.ToAsyncEnumerable())
      {
        await responseStream.WriteAsync(new SingleDataResponse
        {
          Response = new Data
          {
            Metadata = new Metadata
            {
              DataId = res.Metadata!.DataId,
              Location = res.Metadata!.Location,
              SensorName = res.Metadata!.SensorName
            },
            Temperature = res.Temperature,
            Humidity = res.Humidity,
            WaterLevel = res.WaterLevel,
            K = res.K,
            P = res.P,
            N = res.N,
            WateringPlantPumpON = res.WateringPumpOn
          },
          Timestamp = res.Timestamp.ToString("O")
        }
        );
      }
    }
    catch (RpcException)
    {
      throw;
    }
    catch (Exception ex)
    {
      throw new RpcException(new Status(StatusCode.Internal, $"Server error: {ex.Message}"));
    }
  }
  public override async Task<FeedbackResponse> UpdateData(UpdateRequest request, ServerCallContext context)
  {
    try
    {
      var collection = _mongo.GetCollection<DataModel>("iot_data_timeseries");

      var filter = Builders<DataModel>.Filter.Eq(x => x.Metadata!.DataId, request.DataId);
      var data = await collection.Find(filter).FirstOrDefaultAsync();

      if (data == null)
        throw new RpcException(new Status(StatusCode.NotFound, "Data not found, check the data_id!"));

      var update = Builders<DataModel>.Update.Set(x => x.Metadata!.Location, request.NewLocation);
      await collection.UpdateManyAsync(filter, update);

      return await Task.FromResult(new FeedbackResponse
      {
        Feedback = "Data successfully updated!"
      });
    }
    catch (RpcException)
    {
      throw;
    }
    catch (Exception ex)
    {
      throw new RpcException(new Status(StatusCode.Internal, $"Server error: {ex.Message}"));
    }
  }
  public override async Task<FeedbackResponse> AddData(AddRequest request, ServerCallContext context)
  {
    try
    {
      var collection = _mongo.GetCollection<DataModel>("iot_data_timeseries");

      var maxDataId = await collection
        .Find(FilterDefinition<DataModel>.Empty)
        .SortByDescending(x => x.Metadata!.DataId)
        .Limit(1)
        .FirstOrDefaultAsync();

      int newDataId = maxDataId.Metadata!.DataId + 1;

      var newData = new DataModel
      {
        Metadata = new Models.Metadata
        {
          DataId = newDataId,
          Location = request.Location,
          SensorName = request.SensorName,
          IsDataDeleted = false
        },
        Temperature = request.Temperature,
        Humidity = request.Humidity,
        WaterLevel = request.WaterLevel,
        K = request.K,
        P = request.P,
        N = request.N,
        WateringPumpOn = request.WateringPlantPumpON,
        Timestamp = DateTime.UtcNow,
      };

      await collection.InsertOneAsync(newData);

      return await Task.FromResult(new FeedbackResponse
      {
        Feedback = $"Data added successfully with Id {newDataId}"
      });
    }
    catch (Exception ex)
    {
        throw new RpcException(new Status(StatusCode.Internal, $"Server error: {ex.Message}"));
    }
  }
  public override async Task<FeedbackResponse> DeleteData(RequestById request, ServerCallContext context)
  {
    try
    {
      var collection = _mongo.GetCollection<DataModel>("iot_data_timeseries");

      var filter = Builders<DataModel>.Filter.Eq(x => x.Metadata!.DataId, request.DataId);
      var data = await collection.Find(filter).FirstOrDefaultAsync();

      if (data == null)
        throw new RpcException(new Status(StatusCode.NotFound, "Data not found, check the data_id!"));

      var delete = Builders<DataModel>.Update.Set(x => x.Metadata!.IsDataDeleted, true);
      await collection.UpdateManyAsync(filter, delete);

      return new FeedbackResponse
      {
        Feedback = $"Data with Id {request.DataId} successfully deleted!"
      };
    }
    catch (RpcException)
    {
      throw;
    }
    catch (Exception ex)
    {
      throw new RpcException(new Status(StatusCode.Internal, $"Server error: {ex.Message}"));
    }
  }
  public override async Task<SingleDataResponse> MaxTemperature(RequestByTimeSpan request, ServerCallContext context)
  {
    try
    {
      if (request.StartTime == null || request.EndTime == null)
        throw new RpcException(new Status(StatusCode.InvalidArgument, "StartTime and EndTime must be provided."));

      var collection = _mongo.GetCollection<DataModel>("iot_data_timeseries");
      
      var startTime = request.StartTime.ToDateTime();
      var endTime = request.EndTime.ToDateTime();

      if (startTime > endTime)
      {
        (startTime, endTime) = (endTime, startTime);
      }
      
      var filter = Builders<DataModel>.Filter.And(
        Builders<DataModel>.Filter.Gte(x => x.Timestamp, startTime),
        Builders<DataModel>.Filter.Lte(x => x.Timestamp, endTime),
        Builders<DataModel>.Filter.Eq(x => x.Metadata!.IsDataDeleted, false)
      );

      var maxTempDoc = await collection
        .Find(filter)
        .SortByDescending(x => x.Temperature)
        .Limit(1)
        .FirstOrDefaultAsync();

      if (maxTempDoc == null)
      {
        throw new RpcException(new Status(StatusCode.NotFound, "No data found in the given time range."));
      }

      return new SingleDataResponse
      {
        Response = new Data
        {
          Metadata = new Metadata
          {
            DataId = maxTempDoc.Metadata!.DataId,
            Location = maxTempDoc.Metadata.Location,
            SensorName = maxTempDoc.Metadata!.SensorName
          },
          Temperature = maxTempDoc.Temperature,
          Humidity = maxTempDoc.Humidity,
          WaterLevel = maxTempDoc.WaterLevel,
          K = maxTempDoc.K,
          P = maxTempDoc.P,
          N = maxTempDoc.N,
          WateringPlantPumpON = maxTempDoc.WateringPumpOn
        },
        Timestamp = maxTempDoc.Timestamp.ToString("O")
      };
    }
    catch (RpcException)
    {
        throw;
    }
    catch (Exception ex)
    {
        throw new RpcException(new Status(StatusCode.Internal, $"Server error: {ex.Message}"));
    }
  }
  public override async Task<SingleDataResponse> MinHumidity(RequestByStartDateTime request, ServerCallContext context)
  {
    try
    {
      var collection = _mongo.GetCollection<DataModel>("iot_data_timeseries");

      var endDate = request.DateTime.ToDateTime();
      var startDate = endDate.AddDays(-30);

      var filter = Builders<DataModel>.Filter.And(
        Builders<DataModel>.Filter.Gte(x => x.Timestamp, startDate),
        Builders<DataModel>.Filter.Lte(x => x.Timestamp, endDate),
        Builders<DataModel>.Filter.Eq(x => x.Metadata!.IsDataDeleted, false)
      );

      var minHumidity = await collection
        .Find(filter)
        .SortBy(x => x.Temperature)
        .FirstOrDefaultAsync();

      if (minHumidity == null)
        throw new RpcException(new Status(StatusCode.NotFound, "No data found in the specified range."));

      return await Task.FromResult(new SingleDataResponse
      {
        Response = new Data
        {
          Metadata = new Metadata
          {
            DataId = minHumidity.Metadata!.DataId,
            Location = minHumidity.Metadata!.Location,
            SensorName = minHumidity.Metadata!.SensorName
          },
          Temperature = minHumidity.Temperature,
          Humidity = minHumidity.Humidity,
          WaterLevel = minHumidity.WaterLevel,
          K = minHumidity.K,
          P = minHumidity.P,
          N = minHumidity.N,
          WateringPlantPumpON = minHumidity.WateringPumpOn
        },
        Timestamp = minHumidity.Timestamp.ToString("O")
      });
    }
    catch (RpcException)
    {
      throw;
    }
    catch (System.Exception ex)
    {
      throw new RpcException(new Status(StatusCode.Internal, $"Server error: {ex.Message}"));
    }
  }
  public override async Task AvgTempAndHum(
    IAsyncStreamReader<MonthRequest> requestStream,
    IServerStreamWriter<AvgResponse> responseStream,
    ServerCallContext context)
  {
    try
    {
      var collection = _mongo.GetCollection<DataModel>("iot_data_timeseries");

      await foreach (var request in requestStream.ReadAllAsync())
      {
        try
        {
          if (request.Month < 1 || request.Month > 12)
            throw new RpcException(new Status(StatusCode.InvalidArgument, "Month must be between 1 and 12"));

          var startDate = new DateTime(request.Year, request.Month, 1, 0, 0, 0, DateTimeKind.Utc);
          var endDate = startDate.AddMonths(1);
          
          var filter = Builders<DataModel>.Filter.And(
            Builders<DataModel>.Filter.Gte(x => x.Timestamp, startDate),
            Builders<DataModel>.Filter.Lt(x => x.Timestamp, endDate),
            Builders<DataModel>.Filter.Eq(x => x.Metadata!.IsDataDeleted, false)
          );

          var list = await collection.Find(filter).ToListAsync();

          if (list.Count == 0)
            throw new RpcException(new Status(StatusCode.NotFound, "There is no data for inserted date"));

          double avgTemp = list.Average(x => x.Temperature);
          double avgHum = list.Average(x => x.Humidity);

          await responseStream.WriteAsync(new AvgResponse
          {
            IsValid = true,
            Temperature = avgTemp,
            Humidity = avgHum,
            MonthLabel = $"{request.Year:D4}-{request.Month:D2}",
            ErrorMessage = ""
          });
        }
        catch (RpcException exception)
        {
          await responseStream.WriteAsync(new AvgResponse
          {
            IsValid = false,
            Temperature = 0,
            Humidity = 0,
            MonthLabel = $"{request.Year:D4}-{request.Month:D2}",
            ErrorMessage = exception.Status.Detail
          });
        }
      }
    }
    catch (Exception ex)
    {
        throw new RpcException(new Status(StatusCode.Internal, $"Server error: {ex.Message}"));
    }
  }
  public override async Task<SumResponse> CountWaterPumpOn(RequestByTimeSpan request, ServerCallContext context)
  {
    try
    {
      var collection = _mongo.GetCollection<DataModel>("iot_data_timeseries");
      
      var startTime = request.StartTime.ToDateTime();
      var endTime = request.EndTime.ToDateTime();
      if (startTime > endTime) (startTime, endTime) = (endTime, startTime);

      var filter = Builders<DataModel>.Filter.And(
        Builders<DataModel>.Filter.Gte(x => x.Timestamp, startTime),
        Builders<DataModel>.Filter.Lte(x => x.Timestamp, endTime),
        Builders<DataModel>.Filter.Eq(x => x.Metadata!.IsDataDeleted, false),
        Builders<DataModel>.Filter.Eq(x => x.WateringPumpOn, true)
      );

      var count = await collection.CountDocumentsAsync(filter);

      return await Task.FromResult(new SumResponse
      {
        Count = (int)count
      });
    }
    catch (Exception ex)
    {
      throw new RpcException(new Status(StatusCode.Internal, $"Server error: {ex.Message}"));
    }
  }
}