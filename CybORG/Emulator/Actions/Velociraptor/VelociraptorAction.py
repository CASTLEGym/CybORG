from CybORG.Simulator.Actions import Action
from .VelociraptorInterace import VelociraptorInterface


class VelociraptorAction(Action):

    def __init__(self, credentials_file):

        super().__init__()

        self.credentials_file = credentials_file

    def get_velociraptor_interface(self):
        return VelociraptorInterface.get_velociraptor_interface(self.credentials_file)
