import datetime


def set_timezone_jst(time: datetime.datetime) -> datetime.datetime:
    return time + datetime.timedelta(hours=9)


def jst_now() -> datetime.datetime:
    jst_now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
    return jst_now


ON = 1
OFF = 0


def from_TF_to_10(state) -> int:
    if state == True:
        return ON
    else:
        return OFF


PROMETHEUS_RESPONSE = (200, {"Content-Type": "text/plain; charset=utf-8"})

TIMEZONE = "Asia/Tokyo"

KEY_TIME = "time"

KEY_TYPE = "d1"
VALUE_READ = 0
VALUE_WRITTEN = 1

KEY_TEMPERATURE = "d2"
KEY_HUMIDITY = "d3"
KEY_CO2 = "d4"
COLUMNS_READ = [KEY_TEMPERATURE, KEY_HUMIDITY, KEY_CO2]

KEY_LIGHT = "d5"
KEY_HEATER = "d6"
KEY_MIST = "d7"
KEY_FAN = "d8"
COLUMNS_WRITTEN = [KEY_LIGHT, KEY_HEATER, KEY_MIST, KEY_FAN]


CONVERT = {
    KEY_TEMPERATURE: "温度",
    KEY_HUMIDITY: "湿度",
    KEY_CO2: "二酸化炭素濃度",
    KEY_LIGHT: "LED",
    KEY_HEATER: "ヒーター",
    KEY_MIST: "霧発生器",
    KEY_FAN: "ファン",
}


def check_keys_ok(data: dict) -> bool:
    if KEY_TYPE not in data:
        return False

    if data[KEY_TYPE] == VALUE_READ:
        if set(data.keys()) != set([KEY_TYPE] + COLUMNS_READ):
            return False

    if data[KEY_TYPE] == VALUE_WRITTEN:
        if set(data.keys()) != set([KEY_TYPE] + COLUMNS_WRITTEN):
            return False

    return True
