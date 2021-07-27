from typing import Union

from flask import Blueprint, Markup, redirect, render_template, url_for
from hardware.ssr import SSR

import software.types as tp
from software.database import Database, create_database
from software.flask_ import ThreadingFlask
from software.logger import Logger


class Controller:

    mods = {
        tp.KEY_LIGHT: SSR(pin=12),
        tp.KEY_HEATER: SSR(pin=13),
        tp.KEY_MIST: SSR(pin=14),
        tp.KEY_FAN: SSR(pin=15),
    }

    def __init__(
        self, logger: Logger, database: Database, dbapp: ThreadingFlask, port: int
    ) -> None:
        self.logger = logger

        self.auto = {key: tp.ON for key in self.mods.keys()}
        self.force = {key: tp.OFF for key in self.mods.keys()}
        self.state = {key: tp.ON for key in self.mods.keys()}

        @dbapp.route("/metrics")
        def metrics():
            self.update()
            database.send(self.get_written_data())
            return f"", *tp.PROMETHEUS_RESPONSE

        dbapp.thread_run(port)

        self.app = Blueprint("controller", __name__)
        self.myapp()

    def write(self, key: str, state: Union[bool, int]) -> None:
        output = tp.from_TF_to_10(state)
        self.state[key] = output
        self.mods[key].write(output)

    def auto_state(self, key: str) -> bool:
        SUNRISE = 5
        SUNSET = 17
        TARGET_TEMPERATURE = 25
        TARGET_HUMIDITY = 25

        rdf, wdf = self.logger.read("1s", "1m")

        latest_rdata = dict()
        for key in tp.COLUMNS_READ:
            latest_rdata[key] = rdf.iloc[-1][key]
            latest_rdata[key] = 1

        hour = tp.jst_now().hour

        if key == tp.KEY_LIGHT:
            return SUNSET > hour > SUNRISE
        elif key == tp.KEY_HEATER:
            return latest_rdata[tp.KEY_TEMPERATURE] < TARGET_TEMPERATURE
        elif key == tp.KEY_MIST:
            return (
                latest_rdata[tp.KEY_HUMIDITY] < TARGET_HUMIDITY
                or latest_rdata[tp.KEY_TEMPERATURE] > TARGET_TEMPERATURE
            )
        elif key == tp.KEY_FAN:
            return True
        else:
            return False

    def update(self) -> None:
        for key in self.mods.keys():
            if self.auto[key]:
                self.write(key, self.auto_state(key))
            else:
                self.write(key, self.force[key])

    def get_written_data(self) -> dict:
        wdata = {tp.KEY_TYPE: tp.VALUE_WRITTEN}
        for key in self.mods.keys():
            wdata[key] = self.state[key]
        return wdata

    def myapp(self) -> None:
        @self.app.route("/")
        @self.app.route("/index")
        @self.app.route("/controller")
        def index():
            cards = ""
            modenames = ["ON", "OFF", "AUTO"]

            for key in self.mods.keys():
                cards += '<div class="row">'
                for modename in modenames:
                    if self.auto[key]:
                        mode = "AUTO"
                    elif self.force[key]:
                        mode = "ON"
                    else:
                        mode = "OFF"

                    tmp1 = '<div class="col">'
                    tmp2 = f'<a href="/setmode/{key}/{modename}" class="card">'
                    if modename == mode:
                        tmp3 = '<div class="text-white bg-primary">'
                    else:
                        tmp3 = '<div class="text-white bg-info">'
                    tmp4 = '<div class="card-body"><h5 class="card-title text-center">'
                    tmp5 = f"{tp.CONVERT[key]} {modename}"
                    tmp6 = "</h5></div></div></a></div>"

                    card = tmp1 + tmp2 + tmp3 + tmp4 + tmp5 + tmp6
                    cards += card
                cards += "</div>"
            return render_template("controller.html", cards=Markup(cards))

        @self.app.route("/setmode/<key>/<mode>")
        def setmode(key, mode):
            if mode == "AUTO":
                self.auto[key] = tp.ON
            elif mode == "ON":
                self.auto[key] = tp.OFF
                self.force[key] = tp.ON
            elif mode == "OFF":
                self.auto[key] = tp.OFF
                self.force[key] = tp.OFF

            return redirect(url_for("controller.index"))


if __name__ == "__main__":
    database, dbapp = create_database(port=5100)
    logger = Logger(database, dbapp, port=5101)
    database, dbapp = create_database(port=5102)
    controller = Controller(logger, database, dbapp, port=5103)

    app = ThreadingFlask()
    app.register_blueprint(controller.app)
    app.thread_run(port=5104)
