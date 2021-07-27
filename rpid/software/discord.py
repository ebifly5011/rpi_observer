import json

import info
import requests


class Discord:
    URL = info.Discord_WebhookURL
    HEADERS = {"Content-Type": "application/json"}
    TIMEOUT = 3  # [sec]

    def __init__(self) -> None:
        pass

    def send(self, message: str) -> str:
        try:
            content = {"content": message}
            response = requests.post(
                self.URL,
                json.dumps(content),
                headers=self.HEADERS,
                timeout=self.TIMEOUT,
            )
            code = 0
        except Exception as e:
            response = str(e)
            code = 1

        return response, code


if __name__ == "__main__":
    discord = Discord()
    response, code = discord.send("Hello, World!")
    print(response, code)
