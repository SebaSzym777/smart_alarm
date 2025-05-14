from flask import Flask, render_template, request, jsonify
import paho.mqtt.client as mqtt
import json

app = Flask(__name__)

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

@app.route("/home", methods=["GET", "POST"])
def home():
    if request.method == "GET":
        return render_template("login.html")
    elif request.method == "POST":
        if request.form["password"] == passphrase:
            return render_template("panel.html", ip_alarm=ip_alarm, passphrase=passphrase)
        else:
            return render_template("login.html", error="Nieprawidłowe hasło.")

# Nowa trasa do dynamicznego odczytu ruchu
@app.route("/get_motion_status", methods=["POST"])
def get_motion_status():
    return jsonify(motion_detected=motion_detected)

if __name__ == "__main__":
    app.run(host="0.0.0.0")
