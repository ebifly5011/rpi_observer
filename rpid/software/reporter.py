import software.types as tp
from software.controller import Controller
from software.database import create_database
from software.discord import Discord
from software.logger import Logger
from software.flask_ import ThreadingFlask


class Reporter:
    def __init__(self, logger: Logger, port: int) -> None:
        discord = Discord()

        app = ThreadingFlask()

        @app.route("/metrics")
        def metrics() -> dict:
            rdf, wdf = logger.read("1s", "1d")

            latest_data = {
                tp.KEY_TEMPERATURE: rdf.iloc[-1][tp.KEY_TEMPERATURE],
                tp.KEY_HUMIDITY: rdf.iloc[-1][tp.KEY_HUMIDITY],
                tp.KEY_CO2: rdf.iloc[-1][tp.KEY_CO2],
                tp.KEY_LIGHT: wdf.iloc[-1][tp.KEY_LIGHT],
            }

            for before, after in tp.CONVERT.items():
                try:
                    latest_data[after] = latest_data.pop(before)
                except KeyError:
                    pass

            discord.send(str(latest_data))

            return f"", *tp.PROMETHEUS_RESPONSE

        app.thread_run(port)


if __name__ == "__main__":
    database, dbapp = create_database(port=5100)
    logger = Logger(database, dbapp, port=5101)
    database, dbapp = create_database(port=5102)
    controller = Controller(logger, database, dbapp, port=5103)

    reporter = Reporter(logger, port=5105)
