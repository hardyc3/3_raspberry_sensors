import RPi.GPIO as GPIO
import signal
import sys

class RaspberrySensors:

    GREEN_LED = 37
    RED_LED = 35
    YELLOW_LED = 33
    BUZZER = 40
    TILT_SENSOR = 38
    IR_SENSOR = 12
    NEEDS_CLENUP = False

    def __init__(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(RaspberrySensors.GREEN_LED, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(RaspberrySensors.RED_LED, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(RaspberrySensors.YELLOW_LED, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(RaspberrySensors.BUZZER, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(RaspberrySensors.TILT_SENSOR, GPIO.IN)
        GPIO.setup(RaspberrySensors.IR_SENSOR, GPIO.IN)
        RaspberrySensors.NEEDS_CLEANUP = True

    def main_loop(self):
        print("Starting program")
        print("Tilt the tilt control to activate/deactivate the green and red LED")
        print("Press 111 on the remote to enable the buzzer, press 222 to disable it")
        print("Press 55 to toggle the yellow LED, press any other button and the yellow LED will flash.")
        while True:
            tilt_value = GPIO.input(RaspberrySensors.TILT_SENSOR)
            GPIO.output(RaspberrySensors.BUZZER, tilt_value)
            GPIO.output(RaspberrySensors.GREEN_LED, tilt_value)

            if tilt_value:
                GPIO.output(RaspberrySensors.RED_LED, GPIO.LOW)
            else:
                GPIO.output(RaspberrySensors.RED_LED, GPIO.HIGH)

    def shutdown(self):
        if RaspberrySensors.NEEDS_CLEANUP:
            print("Cleaning up GPIO")
            GPIO.cleanup()
            RaspberrySensors.NEEDS_CLEANUP = False

app = None

def signal_handler(singal, frame):
    print("shutting down")
    if app != None:
        app.shutdown()
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    print("Press Ctrl+c to end program")
    app = RaspberrySensors()
    app.main_loop()

