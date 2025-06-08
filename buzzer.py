# buzzer.py
from gpiozero import PWMOutputDevice
from time import sleep

buzzer = PWMOutputDevice(18)
alarm_running = False

def alarm_beep_loop():
    global alarm_running
    alarm_running = True
    try:
        while alarm_running:
            buzzer.frequency = 1000
            buzzer.value = 0.5  # 50% duty cycle
            sleep(0.2)
            buzzer.off()
            sleep(0.2)
    finally:
        buzzer.off()

def stop_alarm():
    global alarm_running
    alarm_running = False
    buzzer.off()
