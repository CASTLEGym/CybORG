from .ProcessObservation import ProcessObservation


class DiscoverRemoteSystemsObservation(ProcessObservation):

    def __init__(self, process_observation, cidr, ip_address_list):

        super().__init__(process_observation.artifact_info)

        self.cidr = cidr

        self.ip_address_list = ip_address_list