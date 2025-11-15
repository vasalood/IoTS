using System.Text.Json.Serialization;

namespace CommandService.Models;

public class CommandMessage
{
  [JsonPropertyName("sensor_name")]
  public string? SensorName { get; set; }

  [JsonPropertyName("temperature")]
  public double? Temperature { get; set; }

  [JsonPropertyName("command")]
  public string? Command { get; set; }
}