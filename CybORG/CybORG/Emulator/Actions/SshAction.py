from typing import Union

import paramiko

from CybORG.Emulator.Observations.SshObservation import SshObservation

from CybORG.Shared import Observation
from CybORG.Simulator.Actions import Action
from CybORG.Simulator.State import State


class SshAction(Action):

    token_dict = {}

    token_number = 0

    @classmethod
    def get_token(cls) -> str:
        token = 'token' + str(cls.token_number)
        cls.token_number += 1
        return token

    @classmethod
    def get_ssh_connection(cls, token):
        return cls.token_dict.get(token, None)

    def __init__(self, ip_address, username, password):
        super().__init__()

        self.ip_address = ip_address
        self.username = username
        self.password = password

        self.session = None

    def execute(self, state: Union[State, None]) -> Observation:

        ssh_session = paramiko.SSHClient()

        ssh_session.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        for ix in range(0, 3):
            try:
                ssh_session.connect(hostname=self.ip_address, username=self.username, password=self.password + str(ix))
            except Exception:
                print("SSH connection failed (on purpose). Trying again ...")

        try:
            ssh_session.connect(hostname=self.ip_address, username=self.username, password=self.password)
        except Exception:
            print("Real SSH connection failed. Bailing out.")
            return SshObservation(False)

        transport = ssh_session.get_transport()

        sock = transport.sock

        local_socket_info = sock.getsockname()
        remote_socket_info = sock.getpeername()

        command = 'echo $PPID'

        stdin, stdout, stderr = ssh_session.exec_command(command)
        remote_pid = int(stdout.readline().strip())
        stdin.close()
        stdout.close()
        stderr.close()

        command = f"echo {remote_pid} >> malicious_pids.txt"
        stdin, stdout, stderr = ssh_session.exec_command(command)
        stdin.close()
        stdout.close()
        stderr.close()

        token = self.get_token()

        self.token_dict[token] = ssh_session

        return SshObservation(
            True, token, local_socket_info=local_socket_info, remote_socket_info=remote_socket_info, pid=remote_pid
        )
