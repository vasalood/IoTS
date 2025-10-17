using MongoDB.Bson;
using MongoDB.Bson.Serialization.Attributes;

namespace GrpcAgriculture.Models;

public class SensorData
{
    [BsonId] //mapira "_id" polje iz MongoDB
    public ObjectId ObjId { get; set; }

    [BsonElement("Id")] 
    public int DataId { get; set; }

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

    [BsonElement("Fan_actuator_OFF")]
    public int FanActuatorOff { get; set; }

    [BsonElement("Fan_actuator_ON")]
    public int FanActuatorOn { get; set; }

    [BsonElement("Watering_plant_pump_OFF")]
    public int WateringPumpOff { get; set; }

    [BsonElement("Watering_plant_pump_ON")]
    public int WateringPumpOn { get; set; }

    [BsonElement("Water_pump_actuator_OFF")]
    public int WaterPumpOff { get; set; }

    [BsonElement("Water_pump_actuator_ON")]
    public int WaterPumpOn { get; set; }

    // [BsonElement("location")]
    // public string? Location { get; set; }

    // [BsonElement("sensor_id")]
    // public int SensorId { get; set; }

    // [BsonElement("sensor_name")]
    // public string? SensorName { get; set; }
    
}

