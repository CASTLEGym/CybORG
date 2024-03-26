import random
import string
from typing import Union

import paramiko
from pathlib import Path

from CybORG.Emulator.Observations.SshObservation import SshObservation

from CybORG.Shared import Observation
from CybORG.Shared.Actions import Action
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

    def __init__(self, ip_address, username, password, port):
        super().__init__()

        self.ip_address = ip_address
        self.username = username
        self.password = password
        self.port = port

        self.session = None

    def execute(self, state: Union[State, None]) -> Observation:

        if self.port != 22:
            return SshObservation(False)

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

        malicious_file_name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

        malicious_file_content = ''.join(random.choices(string.ascii_uppercase + string.digits, k=1024))

        temp_malicious_file_path = Path("/tmp", malicious_file_name)
        with temp_malicious_file_path.open("w") as fp:
            fp.write(malicious_file_content)

        malicious_file_dir_path = Path("Files")
        malicious_file_path = Path(malicious_file_dir_path, malicious_file_name)

        ssh_session.exec_command(f"rm -f {malicious_file_path}")

        sftp_client = ssh_session.open_sftp()
        try:
            sftp_client.lstat(str(malicious_file_dir_path))
        except:
            sftp_client.mkdir(str(malicious_file_dir_path))

        sftp_client.put(str(temp_malicious_file_path), str(malicious_file_path))

        sftp_client.close()

        temp_malicious_file_path.unlink()

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

