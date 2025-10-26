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
	data_id = metadata.get("DataId")
	sensor_name = metadata.get("SensorName")
	location = metadata.get("Location")

	temp = data.get("Temperature")
	humidity = data.get("Humidity")
	water = data.get("WaterLevel")
	timestamp = data.get("Timestamp")

	common_info = {
		"data_id": data_id,
		"sensor_name": sensor_name,
		"location": location,
		"timestamp": timestamp
	}

	if temp is not None:
		if temp >= 38 and not last_state["High temperature"]:
			anomalies.append({
				"event_type": "High temperature",
				"value": temp,
				"threshold": 38
			} | common_info)            
			last_state["High temperature"] = True

		elif temp < 38 and last_state["High temperature"]:
			anomalies.append({
					"event_type": "Temperature back to normal",
					"value": temp
			} | common_info)      
			last_state["High temperature"] = False

		if temp < 25 and not last_state["Low temperature"]:
			anomalies.append({
					"event_type": "Low temperature",
					"value": temp,
					"threshold": 25
			} | common_info)
			last_state["Low temperature"] = True

		elif temp >= 25 and last_state["Low temperature"]:
			anomalies.append({
				"event_type": "Temperature back to normal",
				"value": temp
			} | common_info)
			last_state["Low temperature"] = False

	if humidity is not None:
		if humidity < 50 and not last_state["Low humidity"]:
			anomalies.append({
				"event_type": "Low humidity",
				"value": humidity,
				"threshold": 50
			} | common_info)
			last_state["Low humidity"] = True

		elif humidity >= 50 and last_state["Low humidity"]:
			anomalies.append({
				"event_type": "Humidity back to normal",
				"value": humidity
			} | common_info)
			last_state["Low humidity"] = False

		if humidity > 80 and not last_state["High humidity"]:
			anomalies.append({
				"event_type": "High humidity",
				"value": humidity,
				"threshold": 80
			} | common_info)
			last_state["High humidity"] = True

		elif humidity <= 80 and last_state["High humidity"]:
			anomalies.append({
				"event_type": "Humidity back to normal",
				"value": humidity
			} | common_info)
			last_state["High humidity"] = False

	if water is not None:
		if water < 25 and not last_state["Low water level"]:
			anomalies.append({
				"event_type": "Low water level",
				"value": water,
				"threshold": 25
			} | common_info)
			last_state["Low water level"] = True

		elif water >= 25 and last_state["Low water level"]:
			anomalies.append({
				"event_type": "Water level back to normal",
				"value": water
			} | common_info)
			last_state["Low water level"] = False

	return anomalies