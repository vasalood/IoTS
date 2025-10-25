using MongoDB.Driver;
using MQTTnet;
using SensorService.Models;
using Newtonsoft.Json;

var mongoClient = new MongoClient("mongodb://mongoadmin:Vasamare123@localhost:27017");
var database = mongoClient.GetDatabase("agriculture_database");
var collection = database.GetCollection<DataModel>("iot_data_timeseries");

var factory = new MqttClientFactory();
var mqttClient = factory.CreateMqttClient();
var mqttOptions = new MqttClientOptionsBuilder()
  .WithTcpServer("localhost", 1883)
  .Build();

await mqttClient.ConnectAsync(mqttOptions, CancellationToken.None);

if (mqttClient.IsConnected)
  Console.WriteLine("Connected to MQTT broker.");

int currentId = 1;
bool running = false;

Console.WriteLine("Press 'S' to start publishing, 'P' to pause.");

while (true)
{
  if (Console.KeyAvailable)
  {
    var key = Console.ReadKey(true).Key;
    if (!running && key == ConsoleKey.S)
    {
      running = true;
      Console.WriteLine("Publishing started.");
    }
    else if (running && key == ConsoleKey.P)
    {
      running = false;
      Console.WriteLine("Publishing paused.");
    }
  }

  if (running)
  {
    var filter = Builders<DataModel>.Filter.And(
      Builders<DataModel>.Filter.Gte("metadata.Id", currentId),
      Builders<DataModel>.Filter.Eq("metadata.is_deleted", false)
    );

    var data = await collection.Find(filter).SortBy(x => x.Metadata!.DataId).FirstOrDefaultAsync();

    if (data != null)
    {
      data.Timestamp = DateTime.Now;

      currentId = data.Metadata!.DataId + 1; 

      var jsonMessage = JsonConvert.SerializeObject(data);

      var message = new MqttApplicationMessageBuilder()
        .WithTopic("sensors/data")
        .WithPayload(jsonMessage)
        .Build();

      await mqttClient.PublishAsync(message, CancellationToken.None);
      Console.WriteLine($"Published ID = {data.Metadata.DataId} at {DateTime.Now}");
      await Task.Delay(3000);
    }
    else
    {
      await Task.Delay(1000);
    }
  }
  else
  {
    await Task.Delay(200); 
  }
}