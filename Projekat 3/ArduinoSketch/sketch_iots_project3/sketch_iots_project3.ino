#include "secrets.h"
#include "visuals.h"
#include <Arduino_MKRIoTCarrier.h>
#include <ArduinoMqttClient.h>
#include <WiFiNINA.h>
#include <ArduinoJson.h>

MKRIoTCarrier carrier;
WiFiClient wifiClient;
MqttClient mqttClient(wifiClient);

void setup() {
  Serial.begin(9600);

  delay(1500);

  if (!carrier.begin())
  {
    Serial.println("Carrier not connected, check connections");
    while (1);
  }

  delay(1500);

  // === WiFi konekcija ===
  Serial.print("Povezivanje na WiFi: ");
  Serial.println(WIFI_SSID);
  WiFi.begin(WIFI_SSID, WIFI_PASS);

  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(500);
  }
  Serial.println("\nWiFi povezan!");
  Serial.print("IP adresa: ");
  Serial.println(WiFi.localIP());

  // === MQTT konekcija ===
  Serial.print("Povezivanje na MQTT broker: ");
  Serial.print(MQTT_BROKER);
  Serial.print(":");
  Serial.println(MQTT_PORT);

  if (!mqttClient.connect(MQTT_BROKER, MQTT_PORT)) {
    Serial.print("MQTT konekcija neuspesna! Code: ");
    Serial.println(mqttClient.connectError());
    while (1);
  }
  Serial.println("MQTT povezan!");

  mqttClient.setId("MKR1010");
}

void loop() {
  mqttClient.poll();

  float temperature = carrier.Env.readTemperature();

  Serial.print("Temperatura: ");
  Serial.print(temperature);
  Serial.println(" °C");

  StaticJsonDocument<128> doc;
  doc["sensor_name"] = SENSOR_NAME;
  doc["temperature"] = temperature;

  String jsonString;
  serializeJson(doc, jsonString);

  Serial.print("MQTT send: ");
  Serial.println(jsonString);
 
  mqttClient.beginMessage(MQTT_TOPIC);
  mqttClient.print(jsonString);
  mqttClient.endMessage();

  delay(3000);
}
