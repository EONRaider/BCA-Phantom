#!/usr/bin/env python3
# https://github.com/EONRaider/BCA-Phantom

__author__ = "EONRaider @ keybase.io/eonraider"

import argparse
import functools
from pathlib import Path
from platform import system
from typing import Container

import PyInstaller.__main__


def pyinstaller(func):
    """Decorator that takes a container of strings returned by a
    function and passes them as arguments to the PyInstaller runner."""
    @functools.wraps(func)
    def build_binary(*args, **kwargs):
        cmd: Container[str] = func(*args, **kwargs)
        PyInstaller.__main__.run(cmd)
    return build_binary


def os_name() -> str:
    """Gets the name of the current operating system."""
    return system().lower()


def os_sep() -> str:
    """Gets the path separator for the current operating system.
    Windows systems use ';' as a separator, whereas macOS/Linux/Unix
    use ':'."""
    return ";" if os_name() == "windows" else ":"


@pyinstaller
def server(args: argparse.Namespace) -> list[str]:
    """Set-up the arguments required by PyInstaller to build the
    server binary."""
    cmd = ["src/server/server.py", "--onefile", "--name", f"{os_name()}_server"]
    if args.server_cert is not None:
        cmd.extend(["--add-data", f"{args.server_cert}{os_sep()}."])
    return cmd


@pyinstaller
def client(args: argparse.Namespace) -> list[str]:
    """Set-up the arguments required by PyInstaller to build the
    client binary."""
    config = {"url": args.url}
    cmd = ["src/client/client.py", "--onefile", "--hidden-import", "config"]
    os: str = os_name()

    if args.ca_cert is None:
        cmd.extend(["--name", f"http_{os}_client"])
    else:  # Client bundles CA certificate file in PEM format
        config.update({"ca_cert": Path(args.ca_cert).name})
        cmd.extend(["--name", f"https_{os}_client",
                    "--add-data", f"{args.ca_cert}{os_sep()}."])

    '''A configuration file named 'client.py' is created with hardcoded 
    server URL and path to CA certificate file, if any, that allows 
    seamless connection of the binary client to the server. This file 
    is bundled in the binary and read on execution.'''
    with open(file="src/client/config.py", mode="w") as config_file:
        for key, value in config.items():
            config_file.write(f"{key} = '{value}'\n")

    return cmd


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    server_parser = subparsers.add_parser("server")
    server_parser.add_argument(
        "--server-cert",
        type=str,
        metavar="<path>",
        help="Path to a file containing the server certificate in PEM format. "
             "This certificate will be packaged with the compiled server "
             "binary for deployment."
    )
    server_parser.set_defaults(func=server)

    client_parser = subparsers.add_parser("client")
    client_parser.add_argument(
        "--url",
        type=str,
        help="Full URL of the server (with optional port number) in the format "
             "'SCHEME://DOMAIN|ADDRESS[:PORT]'. "
             "Ex: http://192.168.0.10:8080 or https://your-domain.com"
    )
    client_parser.add_argument(
        "--ca-cert",
        type=str,
        metavar="<path>",
        help="Path to a file containing the certificate for the Certificate "
             "Authority (CA) in PEM format. This certificate will be packaged "
             "with the compiled client binary for deployment."
    )
    client_parser.set_defaults(func=client)

    _args = parser.parse_args()
    _args.func(_args)
