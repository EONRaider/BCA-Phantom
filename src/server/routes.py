#!/usr/bin/env python3
# https://github.com/EONRaider/BCA-Basic-HTTP-Reverse-Shell

__author__ = "EONRaider @ keybase.io/eonraider"


server_routes = list()


def server_route(func):
    server_routes.append(func.__name__)
    return func


@server_route
def send(data) -> None:
    """Handles POST requests to the /send endpoint."""
    with open('/tmp/file', 'wb') as fd:
        fd.write(data["contents"][0].encode())
    print("File saved as /tmp/file")
