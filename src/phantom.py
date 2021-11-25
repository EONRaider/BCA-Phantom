#!/usr/bin/env python3
# https://github.com/EONRaider/BCA-Phantom

__author__ = "EONRaider @ keybase.io/eonraider"


class Phantom:
    def __init__(self, server_url: str):
        """Base class for servers and clients of the Phantom Reverse
        Shell.

        :param server_url: Full URL for the server (with optional port
            number) in the format 'SCHEME://DOMAIN|ADDRESS[:PORT]'.
            Ex: http://192.168.0.10:8080 or https://your-domain.com
        """
        self.server_url = server_url

    @property
    def server_url(self) -> str:
        """Gets the URL for the server.
        Sets the server URL and splits it into elements (scheme, host
        and port number)."""
        return self._server_url

    @server_url.setter
    def server_url(self, url):
        self._scheme, self._host = url.split("://")
        if self._scheme not in {"http", "https"}:
            raise TypeError(f"Error: Unsupported URL scheme for server "
                            f"connection '{self._scheme}'.")
        try:
            self._host, port = self._host.split(":")
            self._port = self.validate_port(port)
        except ValueError:  # Raised if _host has no ":"
            self._port = 443 if self._scheme == "https" else 80
        self._server_url = url

    @staticmethod
    def validate_port(port) -> int:
        """Validates a port number as being an integer in the closed
        range between 0 and 65535."""
        try:
            port = int(port)
            if not 0 < port < 65536:
                raise SystemExit("Error: Port number values must be within "
                                 "the closed range between 0 and 65535.")
        except TypeError:
            raise SystemExit("Error: Port numbers must be integers.")
        return port
