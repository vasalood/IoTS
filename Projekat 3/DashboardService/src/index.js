import express from "express";
import { createNatsConnection, subscribeNATS } from "./nats.js";
import { createMongoClient } from "./mongo.js";

const NATS_URL = "nats://localhost:4222";
const SUBJECT  = "avg.sensor.data.>";
const MONGO_URL = "mongodb://mongoadmin:Vasamare123@localhost:27017/";
const DB_NAME   = "project_3";
const COLL_NAME = "telemetry_data";

let nc;      // NATS connection
let client;  // Mongo client

function parseDateParam(value) {
  if (!value) return null;

  // ako je broj → timestamp
  if (!isNaN(value)) return new Date(parseInt(value));

  // ako je string → Date ga sam parse-uje
  return new Date(value);
}

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
    const doc = {
      timestamp: new Date(msg.t_end),
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

  const app = express();

  app.get("/", (req, res) => {
    res.json({ status: "ok" });
  });

  app.get("/api/telemetry/latest", async (req, res) => {
    try {
      const limit = parseInt(req.query.limit ?? "50", 10);

      const docs = await col
        .find({})
        .sort({ timestamp: -1 })
        .limit(limit)
        .toArray();

      // možeš da preformatiraš ako želiš
      res.json(docs);
    } catch (err) {
      console.error("[dash] /api/telemetry/latest error:", err);
      res.status(500).json({ error: "Internal server error" });
    }
  });

  app.get("/api/telemetry", async (req, res) => {
    try {
      const from = parseDateParam(req.query.from);
      const to   = parseDateParam(req.query.to);
      const limit = req.query.limit ? parseInt(req.query.limit) : 500;

      const query = {};

      if (from || to) {
        query.timestamp = {};
        if (from) query.timestamp.$gte = from;
        if (to)   query.timestamp.$lte = to;
      }

      const docs = await col
        .find(query)
        .sort({ timestamp: 1 })   // time-series prikaz treba da ide od starijeg ka novijem
        .limit(limit)
        .toArray();

      res.json(docs);
    } catch (err) {
      console.error("[dash] /api/telemetry error:", err);
      res.status(500).json({ error: "Internal server error" });
    }
  });

  const PORT = 4000;

  app.listen(PORT, () => {
    console.log(`[dash] HTTP API listening on http://localhost:${PORT}`);
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