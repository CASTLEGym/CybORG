from typing import Union

import sys
import argparse
import paramiko
from pathlib import Path
import json
import zmq


class SSHConnectionServer:

    def __init__(self, connection_key: str, hostname: str, username: str, private_key_file_path: Union[str, Path]):

        self.socket_path = Path(f"/tmp/ssh_connection_{connection_key}")
        self.hostname = hostname
        self.username = username
        self.private_key = paramiko.RSAKey.from_private_key_file(str(private_key_file_path))

        self.ssh_session = None

    def establish_ssh_session(self):
        self.ssh_session = paramiko.SSHClient()

        self.ssh_session.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        self.ssh_session.connect(hostname=self.hostname, username=self.username, pkey=self.private_key)

    def run(self):

        if self.socket_path.exists():
            try:
                self.socket_path.unlink()
            except Exception:
                if self.socket_path.exists():
                    raise Exception(f"{self.socket_path} exists and cannot be removed in order to use it as a socket")

        context = zmq.Context()
        socket = context.socket(zmq.REP)
        socket.bind(f"ipc://{self.socket_path}")

        self.establish_ssh_session()

        while True:
            json_input = socket.recv_string()

            try:
                json_data = json.loads(json_input)

            except Exception as e:
                print(
                    f"Received input \"{json_input}\" incurred an error on parse: {str(e)}.  Ignoring",
                    file=sys.stderr
                )
                socket.send_string("ERROR")
                continue

            if json_data == "CLOSE":
                self.ssh_session.close()
                socket.close()
                self.socket_path.unlink()
                return

            command = json_data["command"]

            try:
                command_stdin, command_stdout, command_stderr = self.ssh_session.exec_command(command)
                command_stdin.close()

                response_dict = {
                    'stdout': command_stdout.read().decode(),
                    'stderr': command_stderr.read().decode()
                }
                command_stdout.close()
                command_stderr.close()

            except Exception as e:
                try:
                    self.ssh_session.close()
                except Exception:
                    pass

                self.establish_ssh_session()
                socket.send_string("RECONNECT")
                continue

            response = json.dumps(response_dict, indent=4, sort_keys=True)

            socket.send_string(response)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="SSHConnection.py",
        description="Server for communicating over a persistent SSH connection"
    )
    parser.add_argument(
        "connection_key",
        nargs="?",
        help="key used to unique identify ssh connection"
    )
    parser.add_argument(
        "hostname",
        nargs="?",
        help="name or ip-address of host to which to connect"
    )
    parser.add_argument(
        "username",
        nargs="?",
        help="name of user for SSH connection"
    )
    parser.add_argument(
        "private_key_file_path",
        nargs="?",
        help="patht of private RSA key file to be used for the SSH connection"
    )

    args = parser.parse_args()
    ssh_connection = SSHConnectionServer(
        connection_key=args.connection_key,
        hostname=args.hostname,
        username=args.username,
        private_key_file_path=args.private_key_file_path
    )

    ssh_connection.run()
