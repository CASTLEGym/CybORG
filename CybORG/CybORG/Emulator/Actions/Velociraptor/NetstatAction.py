from typing import Union

from CybORG.Shared import Observation
from CybORG.Simulator.State import State

from CybORG.Emulator.Observations.Velociraptor.NetstatObservation import NetstatObservation
from CybORG.Emulator.Actions.Velociraptor.VelociraptorAction import VelociraptorAction


class NetstatAction(VelociraptorAction):

    artifact_name = "Custom.Linux.Network.Netstat"

    def __init__(self, credentials_file, hostname, state_regex=None):

        super().__init__(credentials_file=credentials_file)
        self.hostname = hostname
        if state_regex is None:
            state_regex = "Listening|Established"

        self.environment_dict = {"StateRegex": state_regex}

    def execute(self, state: Union[State, None]) -> Observation:

        velociraptor_interface = self.get_velociraptor_interface()

        client_id = velociraptor_interface.get_client_id_from_hostname(self.hostname)

        output_list = velociraptor_interface.execute_client_artifact(
            client_id, self.artifact_name, self.environment_dict
        )

        return NetstatObservation(
            success=False
        ) if output_list is None else NetstatObservation(
            netstat_list=output_list, success=True
        )
