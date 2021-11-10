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
