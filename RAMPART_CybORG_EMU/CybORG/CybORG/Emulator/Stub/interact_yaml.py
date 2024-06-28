import sys
import argparse
from pathlib import Path
from typing import Union

import zmq


class InteractYAML:

    def __init__(self, yaml_file_path: Union[Path, str]=Path("/etc/state.stub")):

        socket_name = yaml_file_path.replace("/", "_")

        self.yaml_file_path = yaml_file_path
        self.socket_path = Path("/tmp", socket_name)

    def run(self):

        context = zmq.Context()

        socket = context.socket(zmq.REQ)

        if not self.socket_path.is_socket():
            print(f"ERROR:  sock for file {self.yaml_file_path} does not exist", file=sys.stderr)
            sys.exit(1)

        socket.connect(f"ipc://{self.socket_path}")

        total_input = ''
        input = sys.stdin.read(1024)
        while input:
            total_input += input
            input = sys.stdin.read(1024)

        socket.send_string(total_input)

        output_bytes = socket.recv_string()
        print(output_bytes)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="interact_yaml.py",
        description="Query or modify a yaml file being managed by 'manage_yaml.py'"
    )
    parser.add_argument(
        "absolute_yaml_file_path",
        nargs="?",
        default="/etc/status",
        help="Absolute path of YAML file being managed bye `manage_yaml.py`, default=\"/etc/status\""
    )

    args = parser.parse_args()
    if len(args.absolute_yaml_file_path) == 0 or args.absolute_yaml_file_path[0] != "/":
        print(f"{sys.argv[0]}:  Specified file path (\"{args.absolute_yaml_file_path}\") must use absolute")
        sys.exit(1)

    interact_yaml = InteractYAML(args.absolute_yaml_file_path)
    interact_yaml.run()
