import subprocess
from typing import Union

import paramiko
from pathlib import Path

from CybORG.Shared import Observation
from CybORG.Shared.Actions import Action
from CybORG.Simulator.State import State


class DeployDecoy(Action):

    def __init__(self, ip_address,decoy_name, decoy_port,username='ubuntu',password='ubuntu'):
        super().__init__()

        self.ip_address = ip_address
        self.username = username
        self.password = password
        self.decoy_name = decoy_name
        self.decoy_port = decoy_port

    def execute(self, state: Union[State, None]) -> Observation:

        ssh_session = paramiko.SSHClient()

        ssh_session.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            ssh_session.connect(hostname=self.ip_address, username=self.username, password=self.password)
        except Exception:
            print("SSH connection failed. Bailing out.")
            return Observation(False)

        script_dir = Path(__file__).parent

        velociraptor_executables_path = Path(script_dir, "..")

        subprocess.run(
            executable="./gradlew",
            args=["./gradlew", ":Velociraptor:Executables:Decoy:build"],
            cwd=str(velociraptor_executables_path)
        )

        decoy_executable_path = Path(velociraptor_executables_path, "Velociraptor/Executables/Decoy/decoy").absolute()

        sftp_client = ssh_session.open_sftp()
        try:
            sftp_client.stat(str(decoy_executable_path))
        except:
            sftp_client.put(str(decoy_executable_path), self.decoy_name)
        sftp_client.close()

        ssh_session.exec_command(f"chmod +x {self.decoy_name} ; PATH=\".:$PATH\" doas {self.decoy_name} {self.decoy_port}")

        return Observation(True)
