import os
import time
from picamera import PiCamera


class Camera(PiCamera):
    def __init__(self) -> None:
        super().__init__()
        self.dir_ = f"{time.time()}"
        os.makedirs(f"/home/pi/rpid/pictures/{self.dir_}", exist_ok=True)

    def pcapture(self) -> None:
        self.start_preview()
        self.capture(f"/home/pi/rpid/pictures/{self.dir_}/{time.time()}.jpg")
        self.stop_preview()


if __name__ == "__main__":
    camera = Camera()
    camera.pcapture()
