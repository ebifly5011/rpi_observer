import time

import RPi.GPIO as GPIO


class WaterDetector:
    def __init__(self, pin: int) -> None:
        self.__pin = pin
        GPIO.setup(self.__pin, GPIO.IN, GPIO.PUD_DOWN)

    def read(self) -> int:
        return int(not bool(GPIO.input(self.__pin)))


if __name__ == "__main__":
    try:
        GPIO.setmode(GPIO.BCM)
        waterdetector = WaterDetector(pin=5)
        while True:
            time.sleep(1)
            is_detected = waterdetector.read()
            print(is_detected)
    except KeyboardInterrupt:
        GPIO.cleanup()
