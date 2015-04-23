# Create the database.
import sqlite3

db = sqlite3.connect('ssids.db')
cursor = db.cursor()

cursor.execute('''CREATE TABLE mac_to_ssid
			(mac, ssid)''')

db.commit()
db.close()
