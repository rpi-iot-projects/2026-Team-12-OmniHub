# OmniHub: IoT Smart Climate Control System

OmniHub is an integrated IoT solution designed to monitor and regulate environmental variables in real-time. Developed as part of a senior engineering initiative at RPI, this system leverages a Raspberry Pi, DHT sensors, and Kasa Smart devices to maintain ideal climate conditions through automated logic and a web-based dashboard.

## 🚀 Features
* **Real-time Monitoring:** Live temperature and humidity tracking via a DHT11 sensor.
* **Automated Climate Logic:** Intelligent control of fans and humidifiers based on user-defined target thresholds.
* **Kasa Device Integration:** Seamless control of smart plugs (Fans, Humidifiers, and Lights) using the `python-kasa` library.
* **Historical Data Visualization:** Persistent storage of climate data using SQLite, visualized with Chart.js on a responsive dashboard.
* **Manual Overrides:** Web-based toggles for instant manual control of all connected hardware.

## 🛠️ Hardware Requirements
* **Microcontroller:** Raspberry Pi (with GPIO access)
* **Sensor:** DHT11 Temperature and Humidity Sensor (Connected to GPIO D4)
* **Smart Plugs:** 3x TP-Link Kasa Smart Plugs (for Fan, Light, and Humidifier)

## 💻 Tech Stack
* **Backend:** Python 3, Flask, Flask-SocketIO, SQLite3
* **Frontend:** HTML5, Tailwind CSS, Chart.js, Socket.io
* **Libraries:** `adafruit-circuitpython-dht`, `python-kasa`, `asyncio`

## ⚙️ Setup & Installation

### 1. Clone the Repository
```bash
git clone [https://github.com/rpi-iot-projects/2026-Team-12-OmniHub.git](https://github.com/rpi-iot-projects/2026-Team-12-OmniHub.git)
cd 2026-Team-12-OmniHub