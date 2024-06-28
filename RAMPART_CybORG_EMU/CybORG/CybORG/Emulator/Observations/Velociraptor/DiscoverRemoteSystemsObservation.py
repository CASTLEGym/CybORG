from .ProcessObservation import ProcessObservation
from CybORG.Shared.Enums import TrinaryEnum

class DiscoverRemoteSystemsObservation(ProcessObservation):

    def __init__(self, process_observation, cidr, ip_address_list):

        boolean_success = True if process_observation.success == TrinaryEnum.TRUE else False
        super().__init__(process_info=process_observation.artifact_info, success=boolean_success)

        self.cidr = cidr

        self.ip_address_list = ip_address_list