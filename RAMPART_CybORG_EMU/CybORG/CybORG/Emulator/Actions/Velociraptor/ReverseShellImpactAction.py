from typing import Union

from CybORG.Shared import Observation
from CybORG.Simulator.State import State

from .RunProcessAction import RunProcessAction
from CybORG.Emulator.Observations.Velociraptor.ReverseShellObservation import ReverseShellObservation


class ReverseShellImpactAction(RunProcessAction):

    def __init__(
            self,
            credentials_file,
            hostname,
            connection_key,
            reverse_shell_server_port,
            reverse_shell_command
    ):
        self.connection_key = connection_key
        self.reverse_shell_server_port = reverse_shell_server_port
        command = f"cd /usr/local/scripts/python;echo \"{reverse_shell_command}\" | " + \
                  f"python ReverseShellTerminalClient.py -n {self.connection_key} -p {self.reverse_shell_server_port}"

        super().__init__(credentials_file, hostname, command)

    def execute(self, state: Union[State, None]) -> Observation:

        observation = super().execute(state)
        return ReverseShellObservation(observation, self.connection_key, self.reverse_shell_server_port)
