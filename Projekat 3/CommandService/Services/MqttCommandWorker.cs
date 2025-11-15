using System.Text;
using System.Text.Json;
using Microsoft.Extensions.Hosting;
using MQTTnet;
using CommandService.Models;

namespace CommandService.Services;

public class MqttCommandWorker : BackgroundService
{
  private readonly WebSocketHub _hub;

  private IMqttClient? _client;

  private bool _acOn;

  private bool _stopping;

  private const string BrokerHost = "localhost"; 
  private const int BrokerPort = 1883;
  private const string CommandTopic = "data/command";

  public MqttCommandWorker(WebSocketHub hub)
  {
    _hub = hub;
    _acOn = true;
    _stopping = false;
  }

  protected override async Task ExecuteAsync(CancellationToken stoppingToken)
  {
    try
    {
      var factory = new MqttClientFactory();
      _client = factory.CreateMqttClient();

      var options = new MqttClientOptionsBuilder()
        .WithTcpServer(BrokerHost, BrokerPort)
        .WithClientId("CommandService")
        .Build();

      _client.ApplicationMessageReceivedAsync += async e =>
      {
        if (_stopping) return;

        try
        {
          var payload = Encoding.UTF8.GetString(e.ApplicationMessage.Payload);

          Console.WriteLine($"[mqtt] Received: {payload}");

          CommandMessage? msg = null;
          try
          {
            var list = JsonSerializer.Deserialize<List<CommandMessage>>(payload);
            msg = list?.FirstOrDefault();
          }
          catch
          {
            Console.WriteLine("[mqtt] Invalid JSON, skipping");
            return;
          }
          
          if (msg is null)
          {
            Console.WriteLine("[mqtt] Empty command list, skipping.");
            return;
          }

          if (msg.Command is null)
          {
            return;
          }

          bool shouldBroadcast = false;

          if (msg.Command == "TURN_ON_AC")
          {
            if (!_acOn)
            {
              _acOn = true;
              shouldBroadcast = true;
              //Console.WriteLine("AAAAAAAA" + _acOn);
            }
          }
          else if (msg.Command == "TURN_OFF_AC")
          {
            if (_acOn)   // klima je bila uključena → sada je isključujemo
            {
              _acOn = false;
              shouldBroadcast = true;
              //Console.WriteLine("AAAAAAAA" + _acOn);
            }
          }

          if (!shouldBroadcast)
          {
            Console.WriteLine("[mqtt] Command ignored (state unchanged).");
            return;
          }

          var uiPayload = JsonSerializer.Serialize(new
          {
            sensorName = msg.SensorName,
            temperature = msg.Temperature,
            command = msg.Command,
            acState = _acOn ? "AC_ON" : "AC_OFF",
            timestamp = DateTime.UtcNow
          });

          await _hub.BroadcastAsync(uiPayload, stoppingToken);
        }
        catch (Exception ex)
        {
          Console.WriteLine($"[mqtt] Error: {ex.Message}");
        }
      };

      await _client.ConnectAsync(options, stoppingToken);
      Console.WriteLine("[mqtt] Connected to broker.");

      await _client.SubscribeAsync(CommandTopic, MQTTnet.Protocol.MqttQualityOfServiceLevel.AtMostOnce, stoppingToken);
      Console.WriteLine($"[mqtt] Subscribed to {CommandTopic}");
      Console.WriteLine("AAAAAAAA" + _acOn);

      while (!stoppingToken.IsCancellationRequested)
      {
        await Task.Delay(1000, stoppingToken);
      }
    }
    catch (OperationCanceledException) when (stoppingToken.IsCancellationRequested)
    {
      Console.WriteLine("[mqtt] Cancellation requested, shutting down worker...");
    }
  }

  public override async Task StopAsync(CancellationToken cancellationToken)
  {
    _stopping = true;

    if (_client != null)
    {
      try
      {
        if (_client.IsConnected)
        {
          await _client.DisconnectAsync(cancellationToken: CancellationToken.None);
          Console.WriteLine("[mqtt] Disconnected from broker.");
        }
      }
      catch (OperationCanceledException)
      {
        Console.WriteLine("[mqtt] Disconnect canceled, ignoring.");
      }
      catch (Exception ex)
      {
        Console.WriteLine($"[mqtt] Error during disconnect: {ex.Message}");
      }
    }

    await base.StopAsync(cancellationToken);
  }
}
