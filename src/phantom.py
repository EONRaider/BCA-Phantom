#!/usr/bin/env python3
# https://github.com/EONRaider/BCA-Phantom

__author__ = "EONRaider @ keybase.io/eonraider"

from urllib.parse import urlparse


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
        Sets the server URL and splits it into its elements (scheme,
        hostname and port number)."""
        return self._server_url

    @server_url.setter
    def server_url(self, url):
        url = urlparse(url)
        self._scheme = url.scheme
        if self._scheme not in {"http", "https"}:
            raise TypeError(f"Error: Unsupported URL scheme for server "
                            f"connection '{self._scheme}'.")
        self._host = url.hostname
        if url.port is None:
            self._port = 443 if self._scheme == "https" else 80
        else:
            self._port = url.port
        self._server_url = url.geturl()
