from time import sleep
from typing import Tuple

import pandas as pd

import software.types as tp
from software.db.prometheus import Prometheus, create_prometheus_flaskapp
from software.flask_ import ThreadingFlask


class Database:
    def __init__(self, prometheus: Prometheus) -> None:
        self.prometheus = prometheus

    def send(self, data: dict) -> None:
        self.prometheus.send(data)

    def read(self, offset: str, timespan: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
        rdfp, wdfp = self.prometheus.read(offset, timespan)

        return rdfp, wdfp


def create_database(port: int) -> Tuple[Database, ThreadingFlask]:

    promapp, prometheus = create_prometheus_flaskapp()

    promapp.thread_run(port)

    database = Database(prometheus)
    dbapp = ThreadingFlask()

    return database, dbapp


if __name__ == "__main__":
    database, dbapp = create_database(port=5100)

    @dbapp.route("/metrics")
    def metrics() -> dict:
        rdata = {
            tp.KEY_TYPE: tp.VALUE_READ,
            tp.KEY_TEMPERATURE: 1,
            tp.KEY_HUMIDITY: 1,
            tp.KEY_CO2: 1,
        }
        wdata = {tp.KEY_TYPE: tp.VALUE_WRITTEN, tp.KEY_LIGHT: 1}

        database.send(rdata)
        database.send(wdata)

        return f"", *tp.PROMETHEUS_RESPONSE

    dbapp.thread_run(port=5101)

    sleep(3)
    rdfp, wdfp = database.read("1s", "1m")
    print(rdfp)
    print(wdfp)
