from typing import Union

from CybORG.Shared import Observation
from CybORG.Simulator.State import State

from CybORG.Emulator.Observations.Velociraptor.ProcessObservation import ProcessObservation
from CybORG.Emulator.Actions.Velociraptor.VelociraptorAction import VelociraptorAction


class RunProcessAction(VelociraptorAction):

    artifact_name = "Linux.Sys.BashShell"

    def __init__(self, credentials_file, hostname, command):

        super().__init__(credentials_file=credentials_file)
        self.hostname = hostname
        self.environment_dict = {"Command": f"{command}"}

    def execute(self, state: Union[State, None]) -> Observation:

        velociraptor_interface = self.get_velociraptor_interface()

        client_id = velociraptor_interface.get_client_id_from_hostname(self.hostname)

        output_list = velociraptor_interface.execute_client_artifact(
            client_id, self.artifact_name, self.environment_dict
        )

        return ProcessObservation(
            success=False
        ) if output_list is None else ProcessObservation(
            process_info=output_list[0], success=True
        )
