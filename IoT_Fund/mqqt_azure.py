import paho.mqtt.client as mqtt
from azure.iot.device import IoTHubDeviceClient
import sqlite3
import json
import time
from datetime import datetime
from Crypto.Cipher import AES

# Define the key (must be 16, 24, or 32 bytes long for AES-128, AES-192, or AES-256)
key = b'\x91\x99`\x19\x1b\xc0O\xd7<M\xb5<=v\x17\x92'

# Create an AES cipher object in ECB mode
cipher = AES.new(key, AES.MODE_ECB)

# Azure IoT Hub credentials
iot_hub_conn_str = "HostName=Bramhub.azure-devices.net;DeviceId=Rasp_Bram;SharedAccessKey=QHWXZzlTwZ7LQ+1oi9206eLCb9clJqhPLv3hNkfqsd4="
device_id = "Rasp_Bram"
device_key = "QHWXZzlTwZ7LQ+1oi9206eLCb9clJqhPLv3hNkfqsd4="

# MQTT broker configuration (Use the IP address or hostname of your Raspberry Pi)
mqtt_broker_host = "localhost"  # e.g., "localhost" or "192.168.1.100"
mqtt_topic = "hello"

# MQTT broker authentication credentials
mqtt_username = "admin"
mqtt_password = "admin"

# MQTT end-to-end encryption
encryptionkey = "" #function needs te be made

# SQLite database connection
conn = sqlite3.connect('/home/admin/minoriot-setup/IoT_Fund/sensor_data.db')
cursor = conn.cursor()

# Azure IoT Hub client
iot_hub_client = IoTHubDeviceClient.create_from_connection_string(iot_hub_conn_str)

# Function to modify the date and time format in each string
def modify_string(input_str):
    # Parse the input string as a datetime object with microseconds
    datetime_obj = datetime.strptime(input_str, "%Y-%m-%d %H:%M:%S.%f")

    # Extract components
    day_name = datetime_obj.strftime("%A")
    month_name = datetime_obj.strftime("%B")
    day = datetime_obj.strftime("%d")
    year = datetime_obj.strftime("%Y")
    time = datetime_obj.strftime("%H.%M.%S")

    # Construct a new string with the desired format
    new_str = f"{day_name} {month_name} {day}, {year}, {time}"

    return new_str

# Callback when a message is received from MQTT
def on_message(client, userdata, message):
    try:
        encrypted_msg_bytes = message.payload

        msg_bytes = cipher.decrypt(encrypted_msg_bytes)

        pad_length = msg_bytes[-1]
        message = msg_bytes[:-pad_length]

        decoded_message = message.decode('utf-8')

        payload = json.loads(decoded_message)

        pressure = payload.get("Pressure", 0)  # Check the capitalization of keys
        temperature = payload.get("Temperature", 0)
        humidity = payload.get("Humidity", 0)
        device = payload.get("device", 0)
        time = datetime.now()

        # Print the received values
        print(f"Received MQTT message - Pressure: {pressure}, Temperature: {temperature}, Humidity: {humidity}, Device: {device} at time: {time}")

        # Store data in SQLite database
        cursor.execute("INSERT INTO sensor_data (pressure, temperature, humidity, device, time, sent_to_iot_hub) VALUES (?, ?, ?, ?, ?, 0)",
                       (pressure, temperature, humidity, device, time))
        conn.commit()

    except Exception as e:
        print(f"Error: {str(e)}")

# Set up MQTT client with authentication
mqtt_client = mqtt.Client()
mqtt_client.username_pw_set(username=mqtt_username, password=mqtt_password)
mqtt_client.on_message = on_message

# Connect to MQTT broker
mqtt_client.connect(mqtt_broker_host, 1883, 60)
mqtt_client.subscribe(mqtt_topic)

# Connect to Azure IoT Hub
iot_hub_client.connect()

# Function to send unsent data to Azure IoT Hub
def send_unsent_data_to_iot_hub():
    try:
        cursor.execute("SELECT id, pressure, temperature, humidity, device, time FROM sensor_data WHERE sent_to_iot_hub = 0")
        rows = cursor.fetchall()

        for row in rows:
            data_id, pressure, temperature, humidity, device, time = row

            modified_time = modify_string(time)

            payload = {
                "pressure": pressure,
                "temperature": temperature,
                "humidity": humidity,
                "device": device,
                "time": modified_time
            }
            msg = json.dumps(payload)
            iot_hub_client.send_message(msg)

            # Mark the data as sent to IoT Hub
            cursor.execute("UPDATE sensor_data SET sent_to_iot_hub = 1 WHERE id = ?", (data_id,))
            conn.commit()

    except Exception as e:
        print(f"Error sending data to IoT Hub: {str(e)}")

try:
    while True:
        mqtt_client.loop()
        send_unsent_data_to_iot_hub()  # Check and send unsent data
        time.sleep(1)

except KeyboardInterrupt:
    print("Disconnecting...")
    mqtt_client.disconnect()
    iot_hub_client.disconnect()
    conn.close()
