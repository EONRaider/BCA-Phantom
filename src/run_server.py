from configparser import ConfigParser
from pathlib import Path

from src.server import ShellServer


shell_cfg = Path(__file__).parent.joinpath("shell.cfg")
(cfg := ConfigParser()).read(shell_cfg)
server_cfg = cfg["SERVER"]
certs_cfg = cfg["CERTIFICATES"]

ShellServer(
    host=server_cfg.get("hostname"),
    port=server_cfg.getint("port"),
    server_cert=certs_cfg.get("server-cert", None),
    ca_cert=certs_cfg.get("ca-cert", None),
    ca_private_key=certs_cfg.get("ca-private-key", None)
).execute()
