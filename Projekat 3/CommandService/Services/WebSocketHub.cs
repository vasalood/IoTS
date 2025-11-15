using System.Net.WebSockets;
using System.Text;
using System.Collections.Concurrent;

namespace CommandService.Services;

public class WebSocketHub
{
  private readonly ConcurrentBag<WebSocket> _sockets = new();
  
  public void AddSocket(WebSocket socket)
  {
    _sockets.Add(socket);
  }

  public async Task BroadcastAsync(string message, CancellationToken cancellationToken = default)
  {
    var buffer = Encoding.UTF8.GetBytes(message);

    foreach (var socket in _sockets.Where(s => s.State == WebSocketState.Open))
    {
      await socket.SendAsync(
        buffer,
        WebSocketMessageType.Text,
        endOfMessage: true,
        cancellationToken: cancellationToken
      );
    }
  }
}
