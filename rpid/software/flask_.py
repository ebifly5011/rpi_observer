import threading

from flask import Flask


class ThreadingFlask(Flask):
    def __init__(self):
        super().__init__(
            __name__,
            static_folder="html/static",
            template_folder="html/templates",
        )

    def thread_run(self, port: int):
        thread = threading.Thread(target=self.run, args=("0.0.0.0", port, False))
        thread.start()
