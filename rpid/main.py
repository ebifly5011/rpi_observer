import logging
from time import sleep

from software.controller import Controller
from software.database import create_database
from software.flask_ import ThreadingFlask
from software.logger import Logger
from software.reporter import Reporter

debug = True
# debug = False

# stdout = True
stdout = False

port = 5000
if debug:
    port += 100

if stdout:
    l = logging.getLogger()
    l.addHandler(logging.FileHandler("/dev/null"))

if __name__ == "__main__":
    database, dbapp = create_database(port=port)
    logger = Logger(database, dbapp, port=port + 1)
    database, dbapp = create_database(port=port + 2)
    controller = Controller(logger, database, dbapp, port=port + 3)
    reporter = Reporter(logger, port=port + 5)

    app = ThreadingFlask()
    app.register_blueprint(controller.app)
    app.thread_run(port=port + 4)

    sleep(3)
    print(f"\n-----------------------------")
    print(f"\nFlask: http://localhost:{port + 4}")
    print(f"\n-----------------------------")
