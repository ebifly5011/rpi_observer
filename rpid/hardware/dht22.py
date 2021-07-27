import time
from typing import List

import RPi.GPIO as GPIO


class DHT22Result:
    "DHT22 sensor result returned by DHT22.result"

    ERR_NO_ERROR = 0
    ERR_MISSING_DATA = 1
    ERR_CRC = 2

    def __init__(self) -> None:
        self.unchanged = 100
        self.temperature = -1
        self.humidity = -1

    def update(self, error_code: int, temperature: float, humidity: float) -> None:
        # If there is no error, change the value.
        if error_code == self.ERR_NO_ERROR:
            self.unchanged = 0
            self.temperature = temperature
            self.humidity = humidity
        else:
            self.unchanged += 1


class DHT22:
    "DHT22 sensor reader class for Raspberry"

    def __init__(self, pin: int) -> None:
        self.__pin = pin
        self.result = DHT22Result()
        self.__last_read_time = -1
        self.__interval = 0.1

    def read(self) -> None:
        GPIO.setup(self.__pin, GPIO.OUT)

        # Ensure read interval
        now = time.time()
        if now - self.__last_read_time > self.__interval:
            self.__last_read_time = now
        else:
            return

        # send initial high
        self.__send_and_sleep(GPIO.HIGH, 0.05)

        # pull down to low
        self.__send_and_sleep(GPIO.LOW, 0.0008)

        # change to input using pull up
        GPIO.setup(self.__pin, GPIO.IN, GPIO.PUD_UP)

        # collect data into an array
        data = self.__collect_input()

        # parse lengths of all data pull up periods
        pull_up_lengths = self.__parse_data_pull_up_lengths(data)

        # if bit count mismatch, return error (4 byte data + 1 byte checksum)
        if len(pull_up_lengths) != 40:
            self.result.update(DHT22Result.ERR_MISSING_DATA, 0, 0)
            return

        # calculate bits from lengths of the pull up periods
        bits = self.__calculate_bits(pull_up_lengths)

        # we have the bits, calculate bytes
        the_bytes = self.__bits_to_bytes(bits)

        # calculate checksum and check
        checksum = self.__calculate_checksum(the_bytes)
        if the_bytes[4] != checksum:
            self.result.update(DHT22Result.ERR_CRC, 0, 0)
            return

        # ok, we have valid data

        # The meaning of the return sensor values
        # the_bytes[0]: humidity int
        # the_bytes[1]: humidity decimal
        # the_bytes[2]: temperature int
        # the_bytes[3]: temperature decimal

        temperature = ((the_bytes[2] * 256) + the_bytes[3]) / 10
        humidity = ((the_bytes[0] * 256) + the_bytes[1]) / 10
        self.result.update(DHT22Result.ERR_NO_ERROR, temperature, humidity)

    def __send_and_sleep(self, output: int, sleep: float) -> None:
        GPIO.output(self.__pin, output)
        time.sleep(sleep)

    def __collect_input(self) -> List[int]:
        # collect the data while unchanged found
        unchanged_count = 0

        # this is used to determine where is the end of the data
        max_unchanged_count = 100

        last = -1
        data = []
        while True:
            current = GPIO.input(self.__pin)
            data.append(current)
            if last != current:
                unchanged_count = 0
                last = current
            else:
                unchanged_count += 1
                if unchanged_count > max_unchanged_count:
                    break

        return data

    def __parse_data_pull_up_lengths(self, data: List[int]) -> List[int]:
        STATE_INIT_PULL_DOWN = 1
        STATE_INIT_PULL_UP = 2
        STATE_DATA_FIRST_PULL_DOWN = 3
        STATE_DATA_PULL_UP = 4
        STATE_DATA_PULL_DOWN = 5

        state = STATE_INIT_PULL_DOWN

        lengths = []  # will contain the lengths of data pull up periods
        current_length = 0  # will contain the length of the previous period

        for i in range(len(data)):

            current = data[i]
            current_length += 1

            if state == STATE_INIT_PULL_DOWN:
                if current == GPIO.LOW:
                    # ok, we got the initial pull down
                    state = STATE_INIT_PULL_UP
                    continue
                else:
                    continue
            if state == STATE_INIT_PULL_UP:
                if current == GPIO.HIGH:
                    # ok, we got the initial pull up
                    state = STATE_DATA_FIRST_PULL_DOWN
                    continue
                else:
                    continue
            if state == STATE_DATA_FIRST_PULL_DOWN:
                if current == GPIO.LOW:
                    # we have the initial pull down, the next will be the data pull up
                    state = STATE_DATA_PULL_UP
                    continue
                else:
                    continue
            if state == STATE_DATA_PULL_UP:
                if current == GPIO.HIGH:
                    # data pulled up, the length of this pull up will determine whether it is 0 or 1
                    current_length = 0
                    state = STATE_DATA_PULL_DOWN
                    continue
                else:
                    continue
            if state == STATE_DATA_PULL_DOWN:
                if current == GPIO.LOW:
                    # pulled down, we store the length of the previous pull up period
                    lengths.append(current_length)
                    state = STATE_DATA_PULL_UP
                    continue
                else:
                    continue

        return lengths

    def __calculate_bits(self, pull_up_lengths: List[int]) -> List[bool]:
        # find shortest and longest period
        shortest_pull_up = 1000
        longest_pull_up = 0

        for i in range(0, len(pull_up_lengths)):
            length = pull_up_lengths[i]
            if length < shortest_pull_up:
                shortest_pull_up = length
            if length > longest_pull_up:
                longest_pull_up = length

        # use the halfway to determine whether the period it is long or short
        halfway = shortest_pull_up + (longest_pull_up - shortest_pull_up) / 2
        bits = []

        for i in range(0, len(pull_up_lengths)):
            bit = False
            if pull_up_lengths[i] > halfway:
                bit = True
            bits.append(bit)

        return bits

    def __bits_to_bytes(self, bits: List[bool]) -> List[int]:
        the_bytes = []
        byte = 0

        for i in range(0, len(bits)):
            byte = byte << 1
            if bits[i]:
                byte = byte | 1
            else:
                byte = byte | 0
            if (i + 1) % 8 == 0:
                the_bytes.append(byte)
                byte = 0

        return the_bytes

    def __calculate_checksum(self, the_bytes: List[int]) -> int:
        return the_bytes[0] + the_bytes[1] + the_bytes[2] + the_bytes[3] & 255


if __name__ == "__main__":
    try:
        GPIO.setmode(GPIO.BCM)
        dht22 = DHT22(pin=4)

        while True:
            time.sleep(1)
            dht22.read()

            print(f"DHT22: Unchanged = {dht22.result.is_unchanged}", end=", ")
            print(f"Temp = {dht22.result.temperature:.1f}[deg C]", end=", ")
            print(f"Hum = {dht22.result.humidity:.1f}[%]")

    except KeyboardInterrupt:
        GPIO.cleanup()
