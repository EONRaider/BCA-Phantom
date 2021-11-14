#!/usr/bin/env python3
# https://github.com/EONRaider/BCA-HTTPS-Reverse-Shell

__author__ = "EONRaider @ keybase.io/eonraider"

import argparse
import configparser
import functools

import PyInstaller.__main__


def pyinstaller(func):
    @functools.wraps(func)
    def build_binary(*args, **kwargs):
        PyInstaller.__main__.run(func(*args, **kwargs))
    return build_binary


@pyinstaller
def server(args: argparse.Namespace) -> list[str]:
    cmd = ["server.py", "--onefile"]
    if args.server_cert is not None:
        cmd.extend(["--add-data", f"{args.server_cert}:."])
    return cmd


@pyinstaller
def client(args: argparse.Namespace) -> list[str]:
    config = configparser.ConfigParser()
    config["CLIENT"] = {
        "host": args.host,
        "port": str(args.port),
        "ca-certificate": args.ca_cert
    }

    with open(file="client.cfg", mode="w") as config_file:
        config.write(config_file)

    cmd = ["client.py",
           "--onefile",
           "--add-data", f"{args.ca_cert}:.",
           "--add-data", "client.cfg:."]

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
        "host",
        type=str,
        metavar="<hostname/address>",
        help="Address or hostname of the server to connect to."
    )
    client_parser.add_argument(
        "port",
        type=int,
        metavar="<port>",
        help="Port number exposed by the server."
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
