from typing import Union

from CybORG.Emulator.Observations.Velociraptor.ProcessListingObservation import ProcessListingObservation
from CybORG.Emulator.Actions.Velociraptor.VelociraptorAction import VelociraptorAction
from CybORG.Simulator.State import State


class ProcessListingAction(VelociraptorAction):

    artifact_name = "Generic.System.Pstree"

    def __init__(self, credentials_file, hostname):
        super().__init__(credentials_file=credentials_file)

        self.hostname = hostname

    def execute(self, state: Union[State, None]) -> ProcessListingObservation:

        velociraptor_interface = self.get_velociraptor_interface()

        client_id = velociraptor_interface.get_client_id_from_hostname(self.hostname)

        return self.get_process_listing_observation(velociraptor_interface, client_id)

    @classmethod
    def get_process_listing_observation(cls, velociraptor_interface, client_id):

        process_list = velociraptor_interface.execute_client_artifact(client_id, cls.artifact_name)

        return ProcessListingObservation(success=False) if process_list is None else ProcessListingObservation(
            process_list=process_list, success=True
        )
