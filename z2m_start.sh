#!/bin/bash

# Zabijanie procesu blokującego /dev/ttyACM0
{
  pid=$(lsof -t /dev/ttyACM0)
  if [ -n "$pid" ]; then
    sudo kill -9 "$pid"
  fi
  sudo systemctl stop serial-getty@ttyACM0.service
  sudo systemctl disable serial-getty@ttyACM0.service
} &> /dev/null &

# Zabijanie Flask na porcie 5000
{
  sudo kill -9 $(sudo lsof -t -i:5000)
} &> /dev/null &

# Uruchamianie Zigbee2MQTT
{
  cd /opt/zigbee2mqtt && npm start &> /dev/null
} &

# Uruchamianie Flask (app.py i alarm.py)
{
  cd ~/flask_alarm
  python3 app.py &> /dev/null &
  python3 alarm.py &> /dev/null &
} &
