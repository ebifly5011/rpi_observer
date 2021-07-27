import datetime
from time import sleep
from typing import Dict, List, Tuple

import pandas as pd
import requests
import software.types as tp
from software.flask_ import ThreadingFlask

URL = "http://localhost:9090/api/v1/query?query="

TIMEOUT = 5


class Prometheus:
    def __init__(self) -> None:
        self.data = dict()

    def send(self, data: dict) -> None:
        if not tp.check_keys_ok(data):
            print("key error")
        data.pop(tp.KEY_TYPE)
        self.data.update(data)

    def get_data(self, offset: str, timespan: str, keys: list) -> List[Dict]:
        data = dict()
        data[tp.KEY_TIME] = []
        for key in keys:
            query = URL + key

            json_ = requests.get(
                f"{query}[{timespan}] offset {offset}", timeout=TIMEOUT
            ).json()
            if len(json_["data"]["result"]) > 0:
                values = json_["data"]["result"][0]["values"]
                data[tp.KEY_TIME] = [float(t) for [t, _] in values]
                data[key] = [float(value) for [_, value] in values]
        return data

    def read(self, offset: str, timespan: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
        rdata = self.get_data(offset, timespan, tp.COLUMNS_READ)
        wdata = self.get_data(offset, timespan, tp.COLUMNS_WRITTEN)

        read_df = pd.DataFrame(rdata)
        read_df = read_df.set_index(tp.KEY_TIME)
        read_df.index = read_df.index.map(datetime.datetime.fromtimestamp)

        written_df = pd.DataFrame(wdata)
        written_df = written_df.set_index(tp.KEY_TIME)
        written_df.index = written_df.index.map(datetime.datetime.fromtimestamp)

        return read_df, written_df


def create_prometheus_flaskapp() -> Tuple[ThreadingFlask, Prometheus]:
    app = ThreadingFlask()
    prometheus = Prometheus()

    @app.route("/metrics")
    def metrics():
        resp = ""
        for key, value in prometheus.data.items():
            resp += f"{key}{{}} {value}\n"
        return f"{resp}", *tp.PROMETHEUS_RESPONSE

    return app, prometheus


if __name__ == "__main__":
    app, prometheus = create_prometheus_flaskapp()
    app.thread_run(port=5100)

    rdata = {
        tp.KEY_TYPE: tp.VALUE_READ,
        tp.KEY_TEMPERATURE: 1,
        tp.KEY_HUMIDITY: 1,
        tp.KEY_CO2: 1,
    }
    wdata = {tp.KEY_TYPE: tp.VALUE_WRITTEN, tp.KEY_LIGHT: 1}

    # prometheus.send(rdata)
    # sleep(2)
    # prometheus.send(wdata)
    # sleep(2)

    rdf, wdf = prometheus.read("1s", "1m")
    print(rdf)
    print(wdf)
