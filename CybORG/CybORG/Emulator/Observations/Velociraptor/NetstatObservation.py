from CybORG.Shared import Observation
from CybORG.Emulator.Observations.Velociraptor.DictToAttributes import DictToAttributes


class NetstatInfo(DictToAttributes):

    def __init__(self, netstat_info_dict=None):

        super().__init__(artifact_info=netstat_info_dict)


class NetstatObservation(Observation):

    def __init__(self, netstat_list=None, success=None):

        Observation.__init__(self, success=success)

        self.artifact_info = netstat_list

        if netstat_list is None:
            netstat_list = []

        self.netstat_list = []
        for netstat_info_dict in netstat_list:
            self.netstat_list.append(NetstatInfo(netstat_info_dict=netstat_info_dict))

    def get_netstat_list(self):
        return self.netstat_list
