from mqtt_client.client import start_mqtt_client
import time

if __name__ == "__main__":
	print("Starting Analytics Service...")
	client = start_mqtt_client()

	try:
		while True:
			time.sleep(1)
	except KeyboardInterrupt:
		print("Shutting down Analytics Service...")
		client.loop_stop()
		client.disconnect()
