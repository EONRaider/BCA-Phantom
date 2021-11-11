#!/usr/bin/env python3
# https://github.com/EONRaider/BCA-HTTPS-Reverse-Shell

__author__ = "EONRaider @ keybase.io/eonraider"

"""This module executes the Reverse Shell Server from settings parsed 
from the shell.cfg file found in this same directory."""

from configparser import ConfigParser
from pathlib import Path

from server import ShellServer


def server():
    shell_cfg = Path(__file__).parent.joinpath("shell.cfg")
    (cfg := ConfigParser()).read(shell_cfg)
    server_cfg = cfg["SERVER"]

    ShellServer(
        host=server_cfg.get("hostname"),
        port=server_cfg.getint("port")
    ).execute()


if __name__ == "__main__":
    server()
