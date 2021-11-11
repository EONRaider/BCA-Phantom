import PyInstaller.__main__ as pyinstaller


def build(mode: str):
    commands = {
        "server": "run_server.py "
                  "--onefile "
                  "--add-data shell.cfg:. "
                  "--add-data ca.pem:. "
                  "--add-data server.pem:.",
        "client": "run_client.py "
                  "--onefile "
                  "--add-data shell.cfg:. "
                  "--add-data ca.pem:."
    }
    pyinstaller.run(commands[mode].split(" "))


if __name__ == "__main__":
    import argparse

    modes = ["server", "client"]
    parser = argparse.ArgumentParser()
    parser.add_argument("mode",
                        choices=modes,
                        help="Choose between server and client modes.")

    _args = parser.parse_args()

    build(mode=_args.mode)
