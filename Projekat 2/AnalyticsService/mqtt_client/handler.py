def handle_sensor_data(data):
	anomalies = check_anomalies(data)
	return anomalies

last_state = {
	"High temperature": False,
	"Low temperature": False,
	"Low humidity": False,
	"High humidity": False,
	"Low water level": False
}

def check_anomalies(data):
	anomalies = []
	metadata = data.get("Metadata", {})
	sensor_name = metadata.get("SensorName")
	location = metadata.get("Location")

	temp = data.get("Temperature")
	humidity = data.get("Humidity")
	water = data.get("WaterLevel")
	timestamp = data.get("Timestamp")

	common_info = {
		"sensor_name": sensor_name,
		"location": location,
		"timestamp": timestamp
	}

	if temp is not None and temp > 40:
		anomalies.append({
			"event_type": "High temperature",
			"value": temp,
			"threshold": 40
		} | common_info)

	if temp is not None and temp < 25:
		anomalies.append({
			"event_type": "Low temperature",
			"value": temp,
			"threshold": 25
		} | common_info)

	if humidity is not None and humidity < 50:
		anomalies.append({
			"event_type": "Low humidity",
			"value": humidity,
			"threshold": 50
		} | common_info)

	if humidity is not None and humidity > 80:
		anomalies.append({
			"event_type": "High humidity",
			"value": humidity,
			"threshold": 80
		} | common_info)

	if water is not None and water < 25:
		anomalies.append({
			"event_type": "Low water level",
			"value": water,
			"threshold": 25
		} | common_info)

	return anomalies