using Grpc.Core;
using GrpcAgriculture.Models;
using MongoDB.Driver;

namespace GrpcAgriculture.Services;

public class GreeterService : Greeter.GreeterBase
{
    private readonly ILogger<GreeterService> _logger;
    private readonly DatabaseService _mongo;
    public GreeterService(ILogger<GreeterService> logger, DatabaseService mongo)
    {
        _logger = logger;
        _mongo = mongo;
    }

    public override Task<HelloReply> SayHello(HelloRequest request, ServerCallContext context)
    {
        return Task.FromResult(new HelloReply
        {
            Message = "Hello " + request.Name
        });
    }

    public override async Task<SensorReply> GetSensorData(SensorRequest request, ServerCallContext context)
    {
        var collection = _mongo.GetCollection<SensorData>("iot_data_timeseries");

        var sensor = await collection.Find(x => x.DataId == request.DataId).FirstOrDefaultAsync();

        if (sensor == null)
            throw new RpcException(new Status(StatusCode.NotFound, "Sensor not found"));

        return new SensorReply
        {
            DataId = sensor.DataId,
            Temperature = sensor.Temperature,
            Humidity = sensor.Humidity,
            WaterLevel = sensor.WaterLevel,
            Timestamp = sensor.Timestamp.ToString("yyyy-MM-dd HH:mm:ss"),
        };
    }
}
