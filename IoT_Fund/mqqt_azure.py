
import paho.mqtt.client as mqtt
from azure.iot.device import IoTHubDeviceClient
import sqlite3
import json
import time
import netifaces

# Function to check if the Raspberry Pi is connected to Wi-Fi
def is_connected_to_wifi():
    try:
        interfaces = netifaces.interfaces()
        for iface in interfaces:
            if iface.startswith('wlan'):
                addrs = netifaces.ifaddresses(iface)
                if netifaces.AF_INET in addrs:
                    return True
        return False
    except Exception as e:
        print(f"Error checking Wi-Fi connection: {str(e)}")
        return False

# Azure IoT Hub credentials
iot_hub_conn_str = "HostName=Bramhub.azure-devices.net;DeviceId=Rasp_Bram;SharedAccessKey=QHWXZzlTwZ7LQ+1oi9206eLCb9clJqhPLv3hNkfqsd4="
device_id = "Rasp_Bram"
device_key = "QHWXZzlTwZ7LQ+1oi9206eLCb9clJqhPLv3hNkfqsd4="

# MQTT broker configuration (Use the IP address or hostname of your Raspberry Pi)
mqtt_broker_host = "localhost"  # e.g., "localhost" or "192.168.1.100"
mqtt_topic = "Condition"

# SQLite database connection
conn = sqlite3.connect('sensor_data.db')
cursor = conn.cursor()

# Azure IoT Hub client
iot_hub_client = IoTHubDeviceClient.create_from_connection_string(iot_hub_conn_str)

# Callback when a message is received from MQTT
def on_message(client, userdata, message):
    try:
        payload = json.loads(message.payload.decode())
        pressure = payload.get('pressure', 0)
        temperature = payload.get('temperature', 0)
        humidity = payload.get('humidity', 0)

        # Forward data to Azure IoT Hub
        msg = json.dumps(payload)
        iot_hub_client.send_message(msg)

        # Store data in SQLite database
        cursor.execute("INSERT INTO sensor_data (pressure, temperature, humidity) VALUES (?, ?, ?)",
                       (pressure, temperature, humidity))
        conn.commit()

    except Exception as e:
        print(f"Error: {str(e)}")

# Set up MQTT client
mqtt_client = mqtt.Client()
mqtt_client.on_message = on_message
mqtt_client.connect(mqtt_broker_host, 1883, 60)
mqtt_client.subscribe(mqtt_topic)

# Connect to Azure IoT Hub
iot_hub_client.connect()

try:
    while True:
        if not is_connected_to_wifi():
            print("Wi-Fi connection lost. Storing data locally...")
            break
        mqtt_client.loop()
        time.sleep(1)

except KeyboardInterrupt:
    print("Disconnecting...")
    mqtt_client.disconnect()
    iot_hub_client.disconnect()
    conn.close()



A

A

A

A



D
D
D
D
D
D
D
D
D
D
D
D
D
D

