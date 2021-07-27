from random import random
from time import sleep
from typing import Tuple

import pandas as pd
from hardware.dht22 import DHT22
from hardware.k30_uart import K30

import software.types as tp
from software.database import Database, create_database
from software.flask_ import ThreadingFlask


class Logger:
    def __init__(self, database: Database, dbapp: ThreadingFlask, port: int) -> None:
        self.database = database

        # self.dht22 = DHT22(pin=4)
        # self.k30 = K30()

        @dbapp.route("/metrics")
        def metrics() -> dict:
            # rdata = {
            #     tp.KEY_TYPE: tp.VALUE_READ,
            #     tp.KEY_TEMPERATURE: self.dht22.result.temperature,
            #     tp.KEY_HUMIDITY: self.dht22.result.humidity,
            #     tp.KEY_CO2: self.k30.result,
            # }
            rdata = {
                tp.KEY_TYPE: tp.VALUE_READ,
                tp.KEY_TEMPERATURE: random(),
                tp.KEY_HUMIDITY: 1,
                tp.KEY_CO2: 1,
            }

            self.database.send(rdata)

            return f"", *tp.PROMETHEUS_RESPONSE

        dbapp.thread_run(port)

    def read(self, offset: str, timespan: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
        rdfp, wdfp = self.database.read(offset, timespan)

        return rdfp, wdfp


if __name__ == "__main__":
    database, dbapp = create_database(port=5100)
    logger = Logger(database, dbapp, port=5101)

    sleep(3)
    rdfp, wdfp = logger.read("1s", "1m")
    print(rdfp)
    print(wdfp)
