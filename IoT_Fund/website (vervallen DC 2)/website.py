from flask import Flask, render_template, jsonify, request
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)

# Function to fetch live data for the last 24 hours from the database
@app.route('/fetch-live-data', methods=['POST'])
def fetch_live_data():
    data = request.json
    deviceTypeSelect = data.get('deviceTypeSelect')
    # Calculate the date and time 24 hours ago from the current time
    end_datetime = datetime.now()
    start_datetime = end_datetime - timedelta(hours=24)

    conn = sqlite3.connect('/home/admin/minoriot-setup/IoT_Fund/sensor_data.db')
    c = conn.cursor()

    # Fetch data from the database based on the last 24 hours
    c.execute('SELECT timestamp, temp, switch FROM sensor_data WHERE idmkr = ? AND time >= ? AND time <= ?', (deviceTypeSelect, start_datetime, end_datetime))
    data = c.fetchall()

    conn.close()

    time_data = [row[0] for row in data]
    temperature_data = [row[1] for row in data]
    boolean_data = [row[2] for row in data]

    data = {
        'time': time_data,
        'temperature': temperature_data,
        'boolean_data': boolean_data
    }

    return jsonify(data)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/fetch-custom-data', methods=['POST'])
def fetch_custom_data():
    data = request.json
    start_datetime = data.get('startDatetime')
    end_datetime = data.get('endDatetime')
    deviceTypeSelect = data.get('deviceTypeSelect')
    start_datetime = start_datetime[:10] + ' ' + start_datetime[11:]
    end_datetime = end_datetime[:10] + ' ' + end_datetime[11:]

    conn = sqlite3.connect('/home/admin/minoriot-setup/IoT_Fund/sensor_data.db')
    c = conn.cursor()

    # Fetch data from the database based on the user-defined date and time range
    c.execute('SELECT timestamp, temp, switch FROM sensor_data WHERE idmkr = ? AND timestamp BETWEEN ? AND ?', (deviceTypeSelect, start_datetime, end_datetime))
    data = c.fetchall()

    conn.close()

    time_data = [row[0] for row in data]
    temperature_data = [row[1] for row in data]
    boolean_data = [row[2] for row in data]

    data = jsonify({
        'time': time_data,
        'temperature': temperature_data,
        'boolean_data': boolean_data
    })

    return data

# Modify your Flask app to fetch distinct device types
@app.route('/get-device-types', methods=['GET'])
def get_device_types():
    conn = sqlite3.connect('/home/admin/minoriot-setup/IoT_Fund/sensor_data.db')
    c = conn.cursor()

    # Fetch distinct device types from the database
    c.execute('SELECT DISTINCT idmkr FROM sensor_data')
    data = c.fetchall()

    conn.close()

    device_types = [row[0] for row in data]

    return jsonify(device_types)

if __name__ == '__main__':
    app.run(debug=True)
