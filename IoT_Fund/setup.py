

import sqlite3

# SQLite database connection
conn = sqlite3.connect('sensor_data.db')
cursor = conn.cursor()

# Create a table to store sensor data if it doesn't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS sensor_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pressure REAL,
                    temperature REAL,
                    humidity REAL,
                    device TEXT,
                    time DATE,
                    sent_to_iot_hub INTEGER DEFAULT 0,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )''')

conn.commit()
conn.close()

print("SQLite database 'sensor_data.db' created successfully.")



