import datetime
import re
from time import sleep, time
from typing import Dict, List, Tuple

import info
import pandas as pd
import software.types as tp
from ambient import Ambient as ambi
import threading


def parse_str_to_timedelta(tdstr: str) -> datetime.timedelta:
    td = datetime.timedelta(seconds=0)
    tags = ["w", "d", "h", "m", "s"]
    args = ["weeks", "days", "hours", "minutes", "seconds"]
    try:
        for i, tag in enumerate(tags):
            if re.match(rf"[0-9]+{tag}", tdstr):
                arg = int(re.match(rf"[0-9]+{tag}", tdstr).group()[:-1])
                td = datetime.timedelta(**{args[i]: arg})
                break
    except AttributeError:
        pass

    return td


ID = info.Ambient_ChannelID
WRITEKRY = info.Ambient_WriteKey
READKEY = info.Ambient_ReadKey
USERKEY = info.Ambient_UserKey

TIMEOUT = 5

KEY_CREATED = "created"
TIME_FORMAT_AMBIENT_WRITE = "%Y-%m-%d %H:%M:%S"
TIME_FORMAT_AMBIENT_READ = "%Y-%m-%dT%H:%M:%S.%fZ"


class Ambient(ambi):
    def __init__(self) -> None:
        super().__init__(ID, WRITEKRY, READKEY, USERKEY)

    def send(self, data: dict):
        if not tp.check_keys_ok(data):
            print("key error")
        super().send(data, timeout=TIMEOUT)

    def read(self, offset: str, timespan: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
        sleep(5)
        offset_td = parse_str_to_timedelta(offset)
        timespan_td = parse_str_to_timedelta(timespan)

        jst = tp.jst_now()
        end = jst - offset_td
        start = end - timespan_td

        start = start.strftime(TIME_FORMAT_AMBIENT_WRITE)
        end = end.strftime(TIME_FORMAT_AMBIENT_WRITE)
        resp: List[Dict] = super().read(start=start, end=end, timeout=TIMEOUT)

        df = pd.json_normalize(resp)

        df[KEY_CREATED] = pd.to_datetime(df[KEY_CREATED])
        df = df.rename(columns={KEY_CREATED: tp.KEY_TIME})
        df = df.set_index(tp.KEY_TIME)
        df.index = df.index.tz_convert(tp.TIMEZONE)

        read_df = df[df[tp.KEY_TYPE] == tp.VALUE_READ]
        read_df = read_df.drop([tp.KEY_TYPE] + tp.COLUMNS_WRITTEN, axis=1)

        written_df = df[df[tp.KEY_TYPE] == tp.VALUE_WRITTEN]
        written_df = written_df.drop([tp.KEY_TYPE] + tp.COLUMNS_READ, axis=1)

        return read_df, written_df


ambient = Ambient()

if __name__ == "__main__":

    rdata = {
        tp.KEY_TYPE: tp.VALUE_READ,
        tp.KEY_TEMPERATURE: 1,
        tp.KEY_HUMIDITY: 1,
        tp.KEY_CO2: 1,
    }
    wdata = {tp.KEY_TYPE: tp.VALUE_WRITTEN, tp.KEY_LIGHT: 1}

    ambient.send(rdata)
    ambient.send(wdata)

    rdf, wdf = ambient.read("1s", "1m")
    print(rdf)
    print(wdf)
