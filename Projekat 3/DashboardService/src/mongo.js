import { MongoClient } from "mongodb";

export async function createMongoClient(uri) {
  const client = new MongoClient(uri);
  await client.connect();
  console.log("[mongo] Connected");
  return client;
}