import random
import string
from typing import Union

from CybORG.Emulator.Observations.Velociraptor.ProcessObservation import ProcessObservation
from CybORG.Emulator.Actions.Velociraptor.RunProcessAction import RunProcessAction
from CybORG.Emulator.Observations.Velociraptor.SSHConnectionServerObservation import SSHConnectionServerObservation
from CybORG.Shared import Observation
from CybORG.Simulator.State import State


class SSHConnectionServerAction(RunProcessAction):

    connection_key_size = 10

    @classmethod
    def get_connection_key(cls):
        return ''.join(
            random.SystemRandom().choice(
                string.ascii_uppercase + string.digits
            ) for _ in range(cls.connection_key_size)
        )

# =======
    def __init__(
            self,
            credentials_file,
            hostname,
            remote_hostname,
            remote_username,
            remote_password,
            client_port,
            server_port=22,
            success_probability=0.5
    ):

        self.connection_key = self.get_connection_key()
        self.success_probility = success_probability

        # print('Credential file :',credentials_file,'host:',hostname)
        super().__init__(
            credentials_file=credentials_file,
            hostname=hostname,
            command=f"/home/ubuntu/justinyeh1995/CASTLEGym/castle.2.venv/bin/python3 /home/ubuntu/justinyeh1995/castle-vm/Scripts/SSHConnectionServer.py -n {self.connection_key} " + \
                    f"-m {remote_hostname} -u {remote_username} -p {remote_password} -c {client_port} -d " + \
                    f"-s {server_port} > /dev/null 2>&1 &"
        )

    def execute(self, state: Union[State, None]) -> Observation:
        # print('Executing**')
        if random.random() >= self.success_probility:
           return ProcessObservation(None,False)

        process_observation = super().execute(state)
        # print('**process observation is :',process_observation)
        return SSHConnectionServerObservation(process_observation, self.connection_key)
