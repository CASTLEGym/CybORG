from typing import Union

from CybORG.Simulator.State import State
from CybORG.Emulator.Observations.Velociraptor.ClientListObservation import ClientListObservation
from CybORG.Emulator.Actions.Velociraptor.VelociraptorAction import VelociraptorAction


class ClientListAction(VelociraptorAction):

    def __init__(self, credentials_file):

        super().__init__(credentials_file)

    def execute(self, state: Union[State, None]) -> ClientListObservation:

        velociraptor_interface = self.get_velociraptor_interface()

        client_list = velociraptor_interface.get_client_list()

        return ClientListObservation(client_list, success=True)
