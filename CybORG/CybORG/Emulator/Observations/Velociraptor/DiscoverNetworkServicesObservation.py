from .ProcessObservation import ProcessObservation


class DiscoverNetworkServicesObservation(ProcessObservation):

    def __init__(self, process_observation, ip_address, port_list):

        super().__init__(process_observation.artifact_info, process_observation)

        self.ip_address = ip_address

        self.port_list = port_list