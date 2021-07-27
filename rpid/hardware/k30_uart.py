import time

import serial


class K30:
    def __init__(self, **kwargs) -> None:
        self.__ser = serial.Serial("/dev/serial0", baudrate=9600, timeout=0.1)
        self.__ser.flushInput()
        time.sleep(1)

        self.result = -1
        self.unchanged = 100

    def read(self) -> None:
        self.__ser.write(b"\xFE\x04\x00\x03\x00\x01\xD5\xC5")
        time.sleep(0.1)
        self.__resp = self.__ser.readline()
        if len(self.__resp) > 1:
            high = self.__resp[3]
            low = self.__resp[4]
            self.result = (high * 256) + low
            self.unchanged = 0
        else:
            self.unchanged += 1

    def close(self) -> None:
        self.__ser.close()


if __name__ == "__main__":
    try:
        k30 = K30()
        while True:
            time.sleep(1)
            k30.read()
            print(f"K30: CO2 = {k30.result:.0f}[ppm]")
    except KeyboardInterrupt:
        k30.close()
