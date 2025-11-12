from datetime import datetime, timezone
from collections import defaultdict

class FilterService:
  """
  Tumbling prozor po 'globalnom' satu procesa (ne po uređaju):
  - skuplja temperature u listu
  - po isteku window_sec izračuna avg i pošalje JSON na NATS
  """
  def __init__(self, window_sec: int, subject_prefix: str, nats_publisher):
    self.window_sec = window_sec
    self.subject_prefix = subject_prefix
    self.nats = nats_publisher

    self._bucket = []           # [(ts_utc_iso, temp, device_id, ...)]
    self._window_started_at = None
    self._running = True

  def ingest(self, measure: dict):
    """
    measure očekuje ključeve:
      - temperature (float)
      - sensor_name ili device_id (opciono; ako nema, stavi default)
    Ako Arduino ne šalje timestamp, dodaćemo server-side UTC.
    """
    if not self._running:
      return

    temp = measure.get("temperature")
    if temp is None:
      return  # ignoriši loš uzorak

    sensor_name = measure.get("sensor_name")
    ts = datetime.now(timezone.utc).isoformat()

    # inicijalizuj prozor
    if self._window_started_at is None:
      self._window_started_at = datetime.now(timezone.utc)

    # ubaci uzorak
    self._bucket.append((ts, float(temp), sensor_name))

    # proveri da li je prozor istekao
    elapsed = (datetime.now(timezone.utc) - self._window_started_at).total_seconds()
    if elapsed >= self.window_sec and self._bucket:
      self._flush()

  def _flush(self):
    # izračunaj avg temperature i broj uzoraka
    temps = [t for _, t, _ in self._bucket]
    avg_temp = sum(temps) / len(temps) if temps else None
    count = len(self._bucket)
    
    sensor_name = self._bucket[-1][2] if self._bucket else "unknown"

    t_start = self._window_started_at.isoformat()
    t_end = datetime.now(timezone.utc).isoformat()

    out = {
      "sensor_name": sensor_name,
      "window": {"type": "tumbling", "size_sec": self.window_sec},
      "t_start": t_start,
      "t_end": t_end,
      "avg": {"temperature": avg_temp},
      "count": count,
    }

    subject = f"{self.subject_prefix}.{sensor_name}"
    self.nats.publish(subject, out)  # thread-safe publish

    # resetuj prozor
    self._bucket.clear()
    self._window_started_at = datetime.now(timezone.utc)

  def stop(self):
    self._running = False
    # po želji ispruži i poslednji nepotpuni prozor:
    if self._bucket:
      self._flush()
