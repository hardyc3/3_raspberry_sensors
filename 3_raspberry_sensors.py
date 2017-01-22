#!/usr/bin/python

import RPi.GPIO as GPIO
import time
import signal
import sys
from datetime import datetime

class RaspberrySensors:

    BUTTON_1 = 18451529148598849809
    BUTTON_2 = 18447043141158568209
    BUTTON_5 = 18451546740784890129

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

    def tilt_callback(self, channel):
        tilt_value = GPIO.input(RaspberrySensors.TILT_SENSOR)
        GPIO.output(RaspberrySensors.BUZZER, tilt_value)
        GPIO.output(RaspberrySensors.GREEN_LED, tilt_value)
        if tilt_value:
            GPIO.output(RaspberrySensors.RED_LED, GPIO.LOW)
        else:
            GPIO.output(RaspberrySensors.RED_LED, GPIO.HIGH)

    pulseStarting = True
    startTime = 0
    command = []
    numOnes = 0
    previousVal = 0
    value = 0

    def ir_callback(self, channel):
        if self.pulseStarting:
            self.startTime = datetime.now()
            self.command = []
            self.numOnes = 0
            self.previousVal = 0
            self.pulseStarting = False

        if self.value != self.previousVal:
            now = datetime.now()
            pulseLength = now - self.startTime
            self.startTime = now
            self.command.append((self.previousVal, pulseLength.microseconds))

        if self.value:
            self.numOnes = self.numOnes + 1
        else:
            self.numOnes = 0

        if self.numOnes > 10000:
            self.pulseStarting = True

        self.previousVal = self.value
        self.value = GPIO.input(RaspberrySensors.IR_SENSOR)

        if len(self.command) > 60:
            binaryString = "".join(map(lambda x: "1" if x[1] > 1000 else "0", filter(lambda x: x[0] == 1, self.command)))
            print "binary: " + binaryString
            print "hex: " + hex(int(binaryString, 2))

    def main_loop(self):
        print("Starting program")
        print("Tilt the tilt control to activate/deactivate the green and red LED")
        print("Press 111 on the remote to enable the buzzer, press 222 to disable it")
        print("Press 55 to toggle the yellow LED, press any other button and the yellow LED will flash.")

        try:
        
            GPIO.add_event_detect(RaspberrySensors.TILT_SENSOR, GPIO.BOTH, callback=self.tilt_callback)

            lastButtonPressed = 0
            buttonPressCount = 0

            while True:

                value = 1
                while value:
                   value = GPIO.input(RaspberrySensors.IR_SENSOR)

                startTime = datetime.now()
                command = []
                numOnes = 0
                previousVal = 0
                
                while True:
                    if value != previousVal:
                        # The value has changed, so calculate the length of this run
                        now = datetime.now()
                        pulseLength = now - startTime
                        startTime = now
                        command.append((previousVal, pulseLength.microseconds))

                    if value:
                        numOnes = numOnes + 1
                    else:
                        numOnes = 0

                    # 10000 is arbitrary, adjust as necessary
                    if numOnes > 10000:
                        break
    
                    previousVal = value
                    value = GPIO.input(RaspberrySensors.IR_SENSOR)
          
                if len(command) > 60:
                    binaryString = "".join(map(lambda x: "1" if x[1] > 1000 else "0", filter(lambda x: x[0] == 1, command)))
                    remoteCode = binaryString[:16]
                    buttonCode = binaryString[16:]
                    buttonInt = int(buttonCode, 16)
                    print "remote hex: " + hex(int(remoteCode, 2))
                    print "button hex: " + hex(int(buttonCode, 2))
                    print "button int: " + str(buttonInt)
                    if buttonInt == lastButtonPressed or lastButtonPressed == 0:
                        print "test3"
                        buttonPressCount += 1
                    else:
                        print "test4"
                        buttonPressCount = 1
                    lastButtonPressed = buttonInt
           
         
                print "test1"
                if buttonPressCount == 3 and lastButtonPressed == RaspberrySensors.BUTTON_1:
                    buttonPressCount == 0
                    GPIO.output(RaspberrySensors.BUZZER, GPIO.HIGH)
                elif buttonPressCount == 3 and lastButtonPressed == RaspberrySensors.BUTTON_2:
                    buttonPressCount = 0
                    GPIO.output(RaspberrySensors.BUZZER, GPIO.LOW)
                elif buttonPressCount == 2 and lastButtonPressed == RaspberrySensors.BUTTON_5:
                    buttonPressCount = 0
                    if GPIO.input(RaspberrySensors.YELLOW_LED):
                        GPIO.output(RaspberrySensors.YELLOW_LED, GPIO.LOW)
                    else:
                        GPIO.output(RaspberrySensors.YELLOW_LED, GPIO.HIGH)

        except:
            print("error", sys.exc_info()[0])
            self.shutdown()

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

