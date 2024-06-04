from .ProcessObservation import ProcessObservation
from CybORG.Shared.Enums import TrinaryEnum


class DiscoverNetworkServicesObservation(ProcessObservation):

    def __init__(self, process_observation, ip_address, port_list):

        boolean_success = True if process_observation.success == TrinaryEnum.TRUE else False
        super().__init__(process_info=process_observation.artifact_info, success=boolean_success)

        self.ip_address = ip_address

        self.port_list = port_list