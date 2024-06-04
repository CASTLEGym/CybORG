import sys
import zmq
import argparse
from textwrap import dedent
from pathlib import Path
from typing import Union

import yaml


class ManageYAML:

    query_command_key = "QUERY"
    replace_key = "__REPLACE__"
    modify_command_key = "MODIFY"

    def __init__(self, yaml_file_path: Union[Path, str]=Path("/etc/state.stub")):

        self.yaml_file_path = yaml_file_path
        if not isinstance(self.yaml_file_path, Path):
            self.yaml_file_path = Path(self.yaml_file_path)

        self.old_yaml_file_path = self.yaml_file_path.with_suffix(".old")

        if self.old_yaml_file_path.exists():
            self.yaml_file_path.unlink()
            self.old_yaml_file_path.rename(self.yaml_file_path)
        elif not self.yaml_file_path.exists():
            with self.yaml_file_path.open("w") as _:
                pass

        socket_name = yaml_file_path.replace("/", "_")

        self.socket_path = Path("/tmp", socket_name)

        self.yaml_data = {}

    @classmethod
    def cleanse_yaml_payload_aux(cls, yaml_payload):

        if isinstance(yaml_payload, dict):
            del yaml_payload[cls.replace_key]

            for value in yaml_payload.values():
                cls.cleanse_yaml_payload_aux(value)

    @classmethod
    def cleanse_yaml_payload(cls, yaml_payload):

        cls.cleanse_yaml_payload_aux(yaml_payload)
        return yaml_payload

    @classmethod
    def modify_yaml_aux(cls, yaml_payload, yaml_data):

        if isinstance(yaml_payload, dict):
            if cls.replace_key in yaml_payload:
                return cls.cleanse_yaml_payload(yaml_payload)
        else:
            return yaml_payload

        for key, value in yaml_payload.items():
            yaml_data[key] = cls.modify_yaml_aux(value, yaml_data[key]) \
                if key in yaml_data else cls.cleanse_yaml_payload(value)
            if yaml_data[key] is None:
                del yaml_data[key]

        return yaml_data

    def modify_yaml(self, yaml_payload):
        self.yaml_data = self.modify_yaml_aux(yaml_payload, self.yaml_data)

    @classmethod
    def get_queried_yaml_data_aux(cls, yaml_payload, yaml_data):
        if not isinstance(yaml_payload,dict):
            return yaml_data

        output_yaml = {}
        for key, value in yaml_payload.items():
            if key not in yaml_data:
                continue
            output_yaml[key] = cls.get_queried_yaml_data_aux(value, yaml_data[key])

        return output_yaml

    def get_queried_yaml_data(self, yaml_payload):
        return self.get_queried_yaml_data_aux(yaml_payload, self.yaml_data)

    @classmethod
    def get_error_message(cls, yaml_input):
        return dedent(
            f"""Received input \"{yaml_input}\" must be a single entry dictionary whose key
            is either \"{cls.query_command_key}\" or \"{cls.modify_command_key}\""""
        )

    def run(self):

        with self.yaml_file_path.open("r") as fp:
            self.yaml_data = yaml.safe_load(fp)

        if self.socket_path.exists():
            try:
                self.socket_path.unlink()
            except Exception:
                if self.socket_path.exists():
                    raise Exception(f"{self.socket_path} exists and cannot be removed in order to use it as a socket")

        context = zmq.Context()
        socket = context.socket(zmq.REP)
        socket.bind(f"ipc://{self.socket_path}")

        while True:
            yaml_input = socket.recv_string()

            try:
                yaml_data = yaml.safe_load(yaml_input)

            except Exception as e:
                print(
                    f"Received input \"{yaml_input}\" incurred an error on parse: {str(e)}.  Ignoring",
                    file=sys.stderr
                )
                socket.send_string('')
                continue

            if not isinstance(yaml_data, dict) or len(yaml_data) != 1 or (
                    self.query_command_key not in yaml_data and
                    self.modify_command_key not in yaml_data
            ):
                print(self.get_error_message(yaml_input), file=sys.stderr)
                socket.send_string('')
                continue

            if self.query_command_key in yaml_data:
                command = self.query_command_key
            elif self.modify_command_key in yaml_data:
                command = self.modify_command_key
            else:
                print(self.get_error_message(yaml_input), file=sys.stderr)
                socket.send_string('')
                continue

            yaml_payload = yaml_data[command]

            if command == self.modify_command_key:
                self.modify_yaml(yaml_payload)
                self.yaml_file_path.rename(self.old_yaml_file_path)
                with self.yaml_file_path.open("w") as fp:
                    yaml.dump(self.yaml_data, fp, sort_keys=True, indent=4)
                socket.send_string('')
                continue

            queried_yaml_data = self.get_queried_yaml_data(yaml_payload)
            query_yaml = yaml.dump(queried_yaml_data, sort_keys=True, indent=4)
            socket.send_string(query_yaml)

    def dump_to_file(self):
        self.yaml_file_path.rename(self.old_yaml_file_path)
        with self.yaml_file_path.open("w") as fp:
            yaml.dump(self.yaml_data, fp, sort_keys=True, indent=4)
        self.old_yaml_file_path.unlink()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="manage_yaml.py",
        description="Server for managing a yaml file"
    )
    parser.add_argument(
        "absolute_yaml_file_path",
        nargs="?",
        default="/etc/status",
        help="Absolute path of YAML file to manage, default=\"/etc/status\""
    )

    args = parser.parse_args()
    if len(args.absolute_yaml_file_path) == 0 or args.absolute_yaml_file_path[0] != "/":
        print(
            f"{sys.argv[0]}:  Specified file path (\"{args.absolute_yaml_file_path}\") must use absolute",
            file=sys.stderr
        )
        sys.exit(1)

    manage_yaml = ManageYAML(args.absolute_yaml_file_path)
    manage_yaml.run()