using MongoDB.Driver;
using MQTTnet;
using SensorService.Models;
using Newtonsoft.Json;

var mongoClient = new MongoClient("mongodb://mongoadmin:Vasamare123@mongo-project-2:27017");
var database = mongoClient.GetDatabase("agriculture_database");
var collection = database.GetCollection<DataModel>("iot_data_timeseries");

var factory = new MqttClientFactory();
var mqttClient = factory.CreateMqttClient();
var mqttOptions = new MqttClientOptionsBuilder()
  .WithTcpServer("mosquitto", 1883)
  .Build();

mqttClient.DisconnectedAsync += async e =>
{
  Console.WriteLine("MQTT client disconnected. Reconnecting in 2s...");
  await Task.Delay(2000);
  try
  {
    await mqttClient.ConnectAsync(mqttOptions, CancellationToken.None);
    Console.WriteLine("Reconnected to MQTT broker.");
  }
  catch
  {
    Console.WriteLine("Reconnect failed. Will retry...");
  }
};

await mqttClient.ConnectAsync(mqttOptions, CancellationToken.None);

if (mqttClient.IsConnected)
  Console.WriteLine("Connected to MQTT broker.");

int currentId = 1;
string lastIdFile = "lastId.txt";

if (File.Exists(lastIdFile))
{
    var text = File.ReadAllText(lastIdFile);
    if (int.TryParse(text, out int savedId))
        currentId = savedId;
}

Console.WriteLine("Publishing sensor data...");

while (true)
{
  var filter = Builders<DataModel>.Filter.And(
    Builders<DataModel>.Filter.Gte("metadata.Id", currentId),
    Builders<DataModel>.Filter.Eq("metadata.is_deleted", false)
  );

  try
  {
    var data = await collection.Find(filter).SortBy(x => x.Metadata!.DataId).FirstOrDefaultAsync();

    if (data != null)
    {
      DateTime utcNow = DateTime.UtcNow;
      DateTime truncated = new DateTime(
        utcNow.Year, utcNow.Month, utcNow.Day,
        utcNow.Hour, utcNow.Minute, utcNow.Second,
        utcNow.Millisecond,      
        DateTimeKind.Utc
      );
      data.Timestamp = truncated;

      currentId = data.Metadata!.DataId + 1;

      File.WriteAllText(lastIdFile, currentId.ToString());

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
  catch (Exception ex)
  {
    Console.WriteLine($"Error during publish: {ex.Message}");
    await Task.Delay(1000);
  }
}