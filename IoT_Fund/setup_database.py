





import sqlite3

# Connect to or create the SQLite database
conn = sqlite3.connect('sensor_data.db')
cursor = conn.cursor()

# Create a table to store sensor data
cursor.execute('''CREATE TABLE IF NOT EXISTS sensor_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pressure REAL,
                    temperature REAL,
                    humidity REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )''')

conn.commit()
conn.close()






