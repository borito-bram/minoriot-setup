from flask import Flask, render_template, jsonify, request
import sqlite3
import plotly.graph_objs as go
from datetime import datetime, timedelta
import json

app = Flask(__name__)

# Function to fetch data for the last 14 days from the database
def fetch_data():
    # Calculate the date 14 days ago from today
    fourteen_days_ago = datetime.now() - timedelta(days=14)
    fourteen_days_ago_str = fourteen_days_ago.strftime('%Y-%m-%d %H:%M:%S')

    conn = sqlite3.connect('/home/admin/minoriot-setup/IoT_Fund/sensor_data.db')
    c = conn.cursor()
    
    # Fetch data for the last 14 days
    c.execute('SELECT time, temperature, humidity, pressure FROM sensor_data WHERE time >= ?', (fourteen_days_ago_str,))
    data = c.fetchall()
    
    conn.close()

    time_data = [row[0] for row in data]
    temperature_data = [row[1] for row in data]
    humidity_data = [row[2] for row in data]
    pressure_data = [row[3] for row in data]

    return time_data, temperature_data, humidity_data, pressure_data

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/fetch-custom-data', methods=['POST'])
def fetch_custom_data():
    data = request.json
    start_datetime = data.get('startDatetime')
    end_datetime = data.get('endDatetime')
    start_datetime = start_datetime[:10] + ' ' + start_datetime[11:]
    end_datetime = end_datetime[:10] + ' ' + end_datetime[11:]

    conn = sqlite3.connect('/home/admin/minoriot-setup/IoT_Fund/sensor_data.db')
    c = conn.cursor()

    # Fetch data from the database based on the user-defined date and time range
    c.execute('SELECT timestamp, temperature, humidity, pressure FROM sensor_data WHERE timestamp BETWEEN ? AND ?', (start_datetime, end_datetime))
    data = c.fetchall()

    conn.close()

    time_data = [row[0] for row in data]
    temperature_data = [row[1] for row in data]
    humidity_data = [row[2] for row in data]
    pressure_data = [row[3] for row in data]
    
    data = jsonify({
        'time': time_data,
        'temperature': temperature_data,
        'humidity': humidity_data,
        'pressure': pressure_data
    })

    print(data)

    return data

if __name__ == '__main__':
    app.run(debug=True)
