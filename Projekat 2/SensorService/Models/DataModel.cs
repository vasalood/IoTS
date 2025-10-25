using MongoDB.Bson;
using MongoDB.Bson.Serialization.Attributes;

namespace SensorService.Models;

public class DataModel
{
  [BsonId]
  public ObjectId ObjId { get; set; }

  [BsonElement("metadata")]
  public Metadata? Metadata { get; set; }

  [BsonElement("timestamp")]
  public DateTime Timestamp { get; set; }

  [BsonElement("temperature")]
  public int Temperature { get; set; }

  [BsonElement("humidity")]
  public int Humidity { get; set; }

  [BsonElement("water_level")]
  public int WaterLevel { get; set; }

  [BsonElement("N")]
  public int N { get; set; }

  [BsonElement("P")]
  public int P { get; set; }

  [BsonElement("K")]
  public int K { get; set; }

  [BsonElement("Watering_plant_pump_ON")]
  [BsonRepresentation(BsonType.Int32)]
  public bool WateringPumpOn { get; set; }
}
public class Metadata
{
  [BsonElement("Id")]
  public int DataId { get; set; }

  [BsonElement("location")]
  public string? Location { get; set; }

  [BsonElement("sensor_name")]
  public string? SensorName { get; set; }

  [BsonElement("is_deleted")]
  public bool IsDataDeleted { get; set; }
}
