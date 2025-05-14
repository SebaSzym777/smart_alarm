# na raspberrypi
from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
import time
import paho.mqtt.client as mqtt
import json

app = Flask(__name__)
CORS(app)

alarm_state = False
alarm_status = False

passphrase = "admin123"
MSG_BAD_PASSPHRASE = "Request wasn't successful, passphrase not provided or invalid"
MSG_OK = "Request was successful"

motion_detected = False  # zaktualizowane przez MQTT

def passphrase_ok(data):
    return "passphrase" in data and data["passphrase"] == passphrase

@app.route("/change_alarm_state", methods=["POST"])
def change_alarm_state():
    global alarm_state
    req_data = request.get_json()

    if not passphrase_ok(req_data):
        return jsonify(status="error", message=MSG_BAD_PASSPHRASE)
    
    if "state" not in req_data or not isinstance(req_data["state"], bool):
        return jsonify(status="error", message="ERROR: `state` key not present or invalid")
    else:
        alarm_state = req_data["state"]
        print("Uzbrajam alarm..." if alarm_state else "Rozbrajam alarm...")

    return jsonify(status="ok", message=MSG_OK)

@app.route("/get_alarm_state", methods=["POST"])
def get_alarm_state():
    req_data = request.get_json()
    if not passphrase_ok(req_data):
        return jsonify(status="error", message=MSG_BAD_PASSPHRASE)
    return jsonify(alarm_state=alarm_state, status="ok", message=MSG_OK)

@app.route("/get_alarm_status", methods=["POST"])
def get_alarm_status():
    req_data = request.get_json()
    if not passphrase_ok(req_data):
        return jsonify(status="error", message=MSG_BAD_PASSPHRASE)
    return jsonify(alarm_status=alarm_status, status="ok", message=MSG_OK)

@app.route("/alarm_accept", methods=["POST"])
def alarm_accept():
    global alarm_status
    req_data = request.get_json()
    if not passphrase_ok(req_data):
        return jsonify(status="error", message=MSG_BAD_PASSPHRASE)
    
    actually_accepted = alarm_status
    alarm_status = False
    return jsonify(status="ok", message=MSG_OK, actually_accepted=actually_accepted)

# MQTT handler
def on_mqtt_message(client, userdata, msg):
    global motion_detected
    try:
        payload = json.loads(msg.payload.decode())
        motion_detected = payload.get("occupancy", False)
        print("MQTT motion_detected:", motion_detected)
    except Exception as e:
        print("Błąd przy przetwarzaniu MQTT:", e)

def mqtt_thread():
    client = mqtt.Client()
    client.on_message = on_mqtt_message
    client.connect("localhost", 1883)
    client.subscribe("zigbee2mqtt/czujnik_2")
    client.loop_forever()

def sensor_loop():
    global alarm_status
    SENSOR_INTERVAL_S = 3
    while True:
        if motion_detected and alarm_state and not alarm_status:
            print("Wykryto ruch, uruchamiam alarm!")
            alarm_status = True
        print("Stan alarmu:", "ALARM" if alarm_status else "BRAK ALARMU")
        time.sleep(SENSOR_INTERVAL_S)

if __name__ == "__main__":
    # Start MQTT
    mqtt_threading = threading.Thread(target=mqtt_thread)
    mqtt_threading.daemon = True
    mqtt_threading.start()

    # Start sensor checker
    sensor_thread = threading.Thread(target=sensor_loop)
    sensor_thread.daemon = True
    sensor_thread.start()

    app.run(port=5001, host="0.0.0.0")
