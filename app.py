from flask import Flask, render_template, request, jsonify, url_for, session
import paho.mqtt.client as mqtt
import os
import json

app = Flask(__name__)
app.secret_key = "admin123"
passphrase = "admin123"
ip_alarm = "http://100.115.166.47:5001"

# Zmienna do przechowywania stanu czujnika
motion_detected = False

# Funkcja obsługująca wiadomości MQTT
def on_message(client, userdata, message):
    global motion_detected
    try:
        payload = json.loads(message.payload.decode())
        motion_detected = payload.get("occupancy", False)
    except Exception as e:
        print("Błąd dekodowania MQTT:", e)

# MQTT setup
client = mqtt.Client()
client.on_message = on_message
client.connect("localhost", 1883)
client.subscribe("zigbee2mqtt/czujnik_2")
client.loop_start()

@app.route("/")
def login():
    return render_template("login.html")

@app.route("/devices")
def devices():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return render_template("devices.html")

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
