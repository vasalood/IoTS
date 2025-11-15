using CommandService.Services;

var builder = WebApplication.CreateBuilder(args);

// registrujemo WebSocketHub i background MQTT worker
builder.Services.AddSingleton<WebSocketHub>();
builder.Services.AddHostedService<MqttCommandWorker>();

builder.Services.AddRouting();
builder.Services.AddControllers(); // nije neophodno ali može zatrebati
builder.Services.AddEndpointsApiExplorer();

var app = builder.Build();

// omogućimo serviranje statičkih fajlova iz wwwroot
app.UseDefaultFiles(); // traži index.html automatski
app.UseStaticFiles();

// omogućimo WebSockets
app.UseWebSockets();

app.Map("/ws/commands", async context =>
{
  if (context.WebSockets.IsWebSocketRequest)
  {
    var hub = context.RequestServices.GetRequiredService<WebSocketHub>();
    var socket = await context.WebSockets.AcceptWebSocketAsync();

    hub.AddSocket(socket);

    // držimo konekciju otvorenom dok klijent ne prekine
    var buffer = new byte[1024];
    while (socket.State == System.Net.WebSockets.WebSocketState.Open)
    {
      var result = await socket.ReceiveAsync(buffer, CancellationToken.None);
      if (result.CloseStatus.HasValue)
      {
        await socket.CloseAsync(result.CloseStatus.Value, result.CloseStatusDescription, CancellationToken.None);
        break;
      }
    }
  }
  else
  {
    context.Response.StatusCode = 400;
  }
});

app.Run();
