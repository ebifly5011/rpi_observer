import time
from typing import Union

import RPi.GPIO as GPIO


class SSR:
    def __init__(self, pin: int) -> None:
        self.__pin = pin
        GPIO.setup(
            self.__pin,
            GPIO.OUT,
        )
        self.is_on = 0
        GPIO.output(self.__pin, self.is_on)

    def write(self, is_on: Union[bool, int]) -> None:
        self.is_on = int(is_on)
        GPIO.output(self.__pin, self.is_on)


if __name__ == "__main__":
    try:
        GPIO.setmode(GPIO.BCM)
        ssr = SSR(pin=12)
        is_on = False
        while True:
            is_on = not is_on
            time.sleep(5)
            ssr.write(is_on)
            print(ssr.is_on)
    except KeyboardInterrupt:
        GPIO.cleanup()
