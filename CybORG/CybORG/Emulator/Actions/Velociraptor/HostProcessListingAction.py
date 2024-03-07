from typing import Union

from ProcessListingAction import ProcessListingAction
from CybORG.Emulator.Observations.Velociraptor.HostProcessListingObservation import HostProcessListingObservation
from CybORG.Emulator.Actions.Velociraptor.VelociraptorAction import VelociraptorAction
from CybORG.Simulator.State import State


class HostProcessListingAction(VelociraptorAction):

    def __init__(self, credentials_file):
        super().__init__(credentials_file)

    def execute(self, state: Union[State, None]):

        velociraptor_interface = self.get_velociraptor_interface()

        client_list = velociraptor_interface.get_client_list()

        hostname_process_list_dict = {}
        for client_dict in client_list:
            hostname = client_dict["os_info"]["hostname"]
            client_id = client_dict["client_id"]

            hostname_process_list_dict[hostname] = ProcessListingAction.get_process_listing_observation(
                velociraptor_interface, client_id
            )

        return HostProcessListingObservation(hostname_process_list_dict)
