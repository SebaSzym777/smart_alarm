# app.py
from flask import Flask, render_template, request, jsonify, url_for, session, redirect
import requests


app = Flask(__name__)
app.secret_key = "admin123"
passphrase = "admin123"
ip_alarm = "http://100.115.166.47:5001"

@app.route("/")
def login():
    return render_template("login.html")

@app.route("/devices")
def devices():
    try:
        response = requests.post(f"{ip_alarm}/get_devices_state", json={"passphrase": passphrase})
        data = response.json()
        if data.get("status") == "ok":
            return render_template("devices.html", devices=data["devices"])
        else:
            return render_template("devices.html", devices={})
    except Exception as e:
        return render_template("devices.html", devices={}, error=str(e))


@app.route('/devices_data')
def devices_data():
    try:
        response = requests.post(f"{ip_alarm}/get_devices_state", json={"passphrase": passphrase})
        data = response.json()
        if data.get("status") == "ok":
            return jsonify(data["devices"])
        else:
            return jsonify({})
    except Exception as e:
        return jsonify(error=str(e)), 500


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


@app.route("/get_motion_status", methods=["POST"])
def get_motion_status():
    try:
        response = requests.post(f"{ip_alarm}/get_alarm_status", json={"passphrase": passphrase})
        data = response.json()
        motion_detected = data.get("alarm_status", False)
        return jsonify(motion_detected=motion_detected)
    except Exception as e:
        return jsonify(motion_detected=False, error=str(e))


@app.route("/start_pairing", methods=["POST"])
def start_pairing():
    try:
        response = requests.post(f"{ip_alarm}/start_pairing", json={"passphrase": passphrase})
        response.raise_for_status()
        return jsonify(response.json())
    except requests.RequestException as e:
        return jsonify(message=f"Błąd sieci: {e}"), 500
    except Exception as e:
        return jsonify(message=f"Inny błąd: {str(e)}"), 500
@app.route("/set_device_params", methods=["POST"])
def set_device_params():
    try:
        data = request.json
        data["passphrase"] = passphrase
        response = requests.post(f"{ip_alarm}/set_device_params", json=data)
        return jsonify(response.json())
    except Exception as e:
        return jsonify(message=f"Błąd: {e}"), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
