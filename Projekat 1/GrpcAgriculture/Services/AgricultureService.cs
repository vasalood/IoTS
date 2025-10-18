using Grpc.Core;
using GrpcAgriculture.Models;
using MongoDB.Driver;

namespace GrpcAgriculture.Services;

public class AgricultureService : Agriculture.AgricultureBase
{
  private readonly DatabaseService _mongo;
  public AgricultureService(DatabaseService mongo)
  {
    _mongo = mongo;
  }
  public override Task<SingleDataResponse> GetData(RequestById request, ServerCallContext context)
  {
      return Task.FromResult(new SingleDataResponse());
  }
  public override async Task GetDataByTimeSpan(RequestByTimeSpan request, IServerStreamWriter<Data> responseStream, ServerCallContext context)
  {
      // koristi responseStream.WriteAsync() za slanje svakog Data objekta
  }
  public override Task<SingleDataResponse> UpdateData(RequestById request, ServerCallContext context)
  {
      return Task.FromResult(new SingleDataResponse());
  }
  public override Task<FeedbackResponse> AddData(AddRequest request, ServerCallContext context)
  {
      return Task.FromResult(new FeedbackResponse());
  }
  public override Task<FeedbackResponse> DeleteData(RequestById request, ServerCallContext context)
  {
      return Task.FromResult(new FeedbackResponse());
  }
  public override Task<Data> MaxTemperature(RequestByTimeSpan request, ServerCallContext context)
  {
      return Task.FromResult(new Data());
  }
  public override Task<Data> MinHumidity(RequestByTimeSpan request, ServerCallContext context)
  {
      return Task.FromResult(new Data());
  }
  public override Task<AvgResponse> AvgTempAndHum(RequestByTimeSpan request, ServerCallContext context)
  {
      return Task.FromResult(new AvgResponse());
  }
  public override Task<SumResponse> CountWaterPumpOn(RequestByTimeSpan request, ServerCallContext context)
  {
      return Task.FromResult(new SumResponse());
  }
}