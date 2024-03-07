from CybORG.Shared import Observation
from CybORG.Emulator.Observations.Velociraptor.DictToAttributes import DictToAttributes


class AgentInformation(DictToAttributes):
    def __init__(self, agent_information_dict):
        super().__init__(agent_information_dict)


class OsInfo(DictToAttributes):

    def __init__(self, os_info_dict):
        super().__init__(os_info_dict)


class Client(DictToAttributes):

    def __init__(self, client_dict):

        self.agent_information = None
        self.os_info = None

        super().__init__(client_dict)

        self.agent_information = AgentInformation(self.agent_information)
        self.os_info = OsInfo(self.os_info)


class ClientListObservation(Observation):

    def __init__(self, client_list, success=None):

        super().__init__(success=success)

        self.artifact_info = client_list

        self.client_list = []
        for client_dict in client_list:
            self.client_list.append(Client(client_dict))

    def get_client_list(self):
        return self.client_list
