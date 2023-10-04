from flask import Flask, render_template, jsonify
import sqlite3
import plotly.graph_objs as go
from datetime import datetime, timedelta
import json

app = Flask(__name__)

# Function to fetch data for the last 14 days from the database
def fetch_data():
    # Calculate the date 14 days ago from today
    fourteen_days_ago = datetime.now() - timedelta(hours=1)
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
    time_data, temperature_data, humidity_data, pressure_data = fetch_data()

    # Create Plotly plots
    temperature_plot = go.Scatter(x=time_data, y=temperature_data, mode='lines', name='Temperature')
    humidity_plot = go.Scatter(x=time_data, y=humidity_data, mode='lines', name='Humidity')
    pressure_plot = go.Scatter(x=time_data, y=pressure_data, mode='lines', name='Pressure')

    plot_data = [temperature_plot, humidity_plot, pressure_plot]

    return render_template('index.html', plot_data=plot_data)

@app.route('/refresh-data', methods=['GET'])
def refresh_data():
    # Fetch the latest data for the last 14 days from the database
    time_data, temperature_data, humidity_data, pressure_data = fetch_data()

    # Create new Plotly plots with the refreshed data and convert to dictionaries
    temperature_plot = {
        'x': time_data,
        'y': temperature_data,
        'mode': 'lines',
        'name': 'Temperature'
    }
    humidity_plot = {
        'x': time_data,
        'y': humidity_data,
        'mode': 'lines',
        'name': 'Humidity'
    }
    pressure_plot = {
        'x': time_data,
        'y': pressure_data,
        'mode': 'lines',
        'name': 'Pressure'
    }

    plot_data = [temperature_plot, humidity_plot, pressure_plot]

    return json.dumps(plot_data)  # Convert the list of dictionaries to JSON format

if __name__ == '__main__':
    app.run(debug=True)
