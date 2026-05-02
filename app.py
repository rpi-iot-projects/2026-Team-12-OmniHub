import asyncio
import threading
import time
import sqlite3 # New import
from flask import Flask, render_template
from flask_socketio import SocketIO
import board
import adafruit_dht
from kasa import Discover, Credentials
from datetime import datetime

app = Flask(__name__)
socketio = SocketIO(app)

# --- DATABASE SETUP ---
def init_db():
    with sqlite3.connect("climate_history.db") as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS readings (
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                temperature REAL,
                humidity REAL
            )
        """)
    print("Database Initialized")

def log_to_db(temp, hum):
    try:
        with sqlite3.connect("climate_history.db") as conn:
            conn.execute("INSERT INTO readings (temperature, humidity) VALUES (?, ?)", (temp, hum))
    except Exception as e:
        print(f"DB Log Error: {e}")

# --- GLOBAL SETTINGS ---
target_temp = target_hum = cur_temp = cur_hum = None
manual_fan = manual_hum = False
fan = light = humidifier = None

# --- CONFIGURATION (Sync these names!) ---
KASA_USER = "ivy.weinert@gmail.com"
KASA_PASS = "Dr0ps0fJup!t3r"
fan_ip = "192.168.0.202"
light_ip = "192.168.0.237"
humidifier_ip = "192.168.0.216"

dht_device = adafruit_dht.DHT11(board.D4)

async def init_devices():
    global fan, light, humidifier
    creds = Credentials(KASA_USER, KASA_PASS)
    try:
        fan = await Discover.discover_single(fan_ip, credentials=creds)
        light = await Discover.discover_single(light_ip, credentials=creds)
        humidifier = await Discover.discover_single(humidifier_ip, credentials=creds)
        print("Kasa Devices Connected Successfully")
    except Exception as e:
        print(f"Initialization error: {e}")

async def run_kasa_cmd(device, state):
    if device:
        try:
            await device.update()
            if state: await device.turn_on()
            else: await device.turn_off()
        except Exception as e:
            print(f"Kasa command error: {e}")

def climate_logic_loop():
    global target_temp, target_hum, cur_temp, cur_hum, manual_fan, manual_hum
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    while True:
        if not manual_fan and target_temp is not None and cur_temp is not None:
            loop.run_until_complete(run_kasa_cmd(fan, cur_temp > target_temp))
        if not manual_hum and target_hum is not None and cur_hum is not None:
            loop.run_until_complete(run_kasa_cmd(humidifier, cur_hum < target_hum))
        time.sleep(10)

def sensor_loop():
    global cur_temp, cur_hum
    last_log_time = 0
    while True:
        try:
            cur_temp, cur_hum = dht_device.temperature, dht_device.humidity
            socketio.emit("sensor_update", {
                "temperature": cur_temp, "humidity": cur_hum,
                "target_temp": target_temp, "target_hum": target_hum
            })
            
            # Log to DB every 10 minutes (600 seconds)
            if time.time() - last_log_time > 600:
                log_to_db(cur_temp, cur_hum)
                last_log_time = time.time()
                
        except: pass
        time.sleep(2)

# --- SOCKET EVENTS ---
@app.route("/")
def index():
    return render_template("omnihub.html")

@socketio.on("connect")
def handle_connect():
    # Send historical data to client on connect
    with sqlite3.connect("climate_history.db") as conn:
        cursor = conn.execute("SELECT timestamp, temperature, humidity FROM readings ORDER BY timestamp DESC LIMIT 50")
        history = [{"time": r[0], "temp": r[1], "hum": r[2]} for r in cursor.fetchall()]
        socketio.emit("history_data", history[::-1]) # Send in chronological order

@socketio.on("toggle_light")
def handle_light(state):
    asyncio.run(run_kasa_cmd(light, state))

@socketio.on("toggle_fan_override")
def handle_fan_override(data):
    global manual_fan
    manual_fan = data.get("manual", False)
    if manual_fan:
        asyncio.run(run_kasa_cmd(fan, data.get("state", False)))

@socketio.on("toggle_humidifier_override")
def handle_humidifier_override(data):
    global manual_hum
    manual_hum = data.get("manual", False)
    if manual_hum:
        asyncio.run(run_kasa_cmd(humidifier, data.get("state", False)))

@socketio.on("set_targets")
def handle_targets(data):
    global target_temp, target_hum
    target_temp = float(data["temperature"]) if data["temperature"] else None
    target_hum = float(data["humidity"]) if data["humidity"] else None
    if "light_state" in data:
        is_on = True if data["light_state"] == "on" else False
        asyncio.run(run_kasa_cmd(light, is_on))

if __name__ == "__main__":
    init_db() # Create DB table
    asyncio.run(init_devices())
    threading.Thread(target=sensor_loop, daemon=True).start()
    threading.Thread(target=climate_logic_loop, daemon=True).start()
    socketio.run(app, host="0.0.0.0", port=5000)