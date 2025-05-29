from flask import Flask, render_template, request, jsonify, url_for, session
import paho.mqtt.client as mqtt
import os
import json

app = Flask(__name__)
app.secret_key = "admin123"
passphrase = "admin123"
ip_alarm = "http://100.115.166.47:5001"
devices_state = {}


# Zmienna do przechowywania stanu czujnika
motion_detected = False

# Funkcja obsługująca wiadomości MQTT

def on_message(client, userdata, message):
    global motion_detected, devices_state
    try:
        payload = json.loads(message.payload.decode())
        print(payload)
        # Jeśli payload jest listą, można przetworzyć ją inaczej lub pominąć
        if isinstance(payload, list):
            print("Otrzymano listę zamiast słownika w MQTT:", payload)
            return

        # Aktualizacja stanu ruchu (motion_detected)
        motion_detected = payload.get("occupancy", False)
	
        # Aktualizacja stanu urządzeń - przykładowo, zakładamy, że temat zawiera nazwę urządzenia
        topic_parts = message.topic.split('/')
        if len(topic_parts) >= 2:
            device_name = topic_parts[-1]
            devices_state[device_name] = payload

    except Exception as e:
        print("Błąd dekodowania MQTT:", e)

# MQTT setup
client = mqtt.Client()
client.on_message = on_message
client.connect("localhost", 1883)
client.subscribe("zigbee2mqtt/#")
client.loop_start()

@app.route("/")
def login():
    return render_template("login.html")

@app.route("/devices")
def devices():
    filtered_devices = {k: v for k, v in devices_state.items() if isinstance(v, dict) and ('battery' in v or 'occupancy' in v)}
    return render_template("devices.html", devices=filtered_devices)

@app.route('/devices_data')
def devices_data():
    filtered_devices = {k: v for k, v in devices_state.items() if isinstance(v, dict) and ('battery' in v or 'occupancy' in v)}
    return jsonify(filtered_devices)

@app.route("/home", methods=["GET", "POST"])
def home():
    if request.method == "GET":
        if session.get("logged_in"):
            return render_template("panel.html", ip_alarm=ip_alarm, passphrase=passphrase)
        else:
            return redirect(url_for("login"))
    elif request.method == "POST":
        if request.form["password"] == passphrase:
            session["logged_in"] = True
            return render_template("panel.html", ip_alarm=ip_alarm, passphrase=passphrase)
        else:
            return render_template("login.html", error="Nieprawidłowe hasło.")
# Nowa trasa do dynamicznego odczytu ruchu
@app.route("/get_motion_status", methods=["POST"])
def get_motion_status():
    return jsonify(motion_detected=motion_detected)

if __name__ == "__main__":
    app.run(host="0.0.0.0")
