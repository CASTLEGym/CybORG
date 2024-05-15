import sys
import zmq
import json
import argparse
from pathlib import Path


class SSHConnectionClient:

    def __init__(self, connection_key):

        self.socket_path = Path(f"/tmp/ssh_connection_{connection_key}")
        if not self.socket_path.exists():
            raise Exception(f"SSHConnectionServer with key \"{connection_key}\" does not exist")

    def run(self):

        context = zmq.Context()

        socket = context.socket(zmq.REQ)

        socket.connect(f"ipc://{self.socket_path}")

        total_command = ''
        input_data = sys.stdin.read(1024)
        while len(input_data) > 0:
            total_command += input_data
            input_data = sys.stdin.read(1024)

        total_command = total_command.strip()

        if total_command == "CLOSE":
            json_data = total_command
        else:
            json_data = {
                "command": total_command
            }

        json_string = json.dumps(json_data, indent=4, sort_keys=True)
        socket.send_string(json_string)

        output_bytes = socket.recv_string()

        json_data = json.loads(output_bytes)
        if isinstance(json_data, str):
            print(json_data)
        else:
            print(json_data['output'], end='')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="SSHConnectionClient.py",
        description="Submit commands to an SSHConnectionServer"
    )
    parser.add_argument(
        "connection_key",
        nargs="?",
        help="Key for the SSHConnectionServer"
    )

    args = parser.parse_args()

    ssh_connection_client = SSHConnectionClient(args.connection_key)
    ssh_connection_client.run()
