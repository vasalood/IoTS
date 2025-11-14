import { createNatsConnection, subscribeNATS } from "./nats.js";
import { createMongoClient } from "./mongo.js";

const NATS_URL = "nats://localhost:4222";
const SUBJECT  = "avg.sensor.data.>";
const MONGO_URL = "mongodb://mongoadmin:Vasamare123@localhost:27017/";
const DB_NAME   = "project_3";
const COLL_NAME = "telemetry_data";

let nc;      // NATS connection
let client;  // Mongo client

async function main() {
  console.log("[dash] Starting DashboardService ...");

  // 1) NATS
  nc = await createNatsConnection(NATS_URL);

  // 2) Mongo
  client = await createMongoClient(MONGO_URL);
  const db = client.db(DB_NAME);
  const col = db.collection(COLL_NAME);

  // 3) Obrada poruka sa NATS-a
  subscribeNATS(nc, SUBJECT, async (msg) => {
    // Očekujemo poruku iz FilterService-a, npr:
    // {
    //   sensor_name: "MKR1010_WiFi",
    //   window: { type: "tumbling", size_sec: 15 },
    //   t_start: "...",
    //   t_end: "...",
    //   avg: { temperature: 23.4 },
    //   count: 5
    // }

    // ts -> koristimo t_end (kraj prozora) kao vremensku tačku
    const timestamp = new Date(msg.t_end);
    const doc = {
      timestamp: timestamp,
      metadata: {
        sensor_name: msg.sensor_name,
        window: msg.window
      },
      average_temp: msg.avg,
      count: msg.count
    };

    await col.insertOne(doc);
    console.log("[dash] inserted:", {
      sensor: doc.metadata.sensor_name,
      ts: doc.timestamp.toISOString(),
      avg: doc.average_temp,
      count: doc.count
    });
  });

  // 4) graceful shutdown
  process.on("SIGINT", stop);
  process.on("SIGTERM", stop);
}

async function stop() {
  console.log("\n[dash] Stopping ...");
  try { if (nc) await nc.drain(); } catch {}
  try { if (client) await client.close(); } catch {}
  console.log("[dash] Bye.");
  process.exit(0);
}

main().catch(err => {
  console.error("[dash] Fatal:", err);
  process.exit(1);
});