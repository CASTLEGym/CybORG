from .ProcessObservation import ProcessObservation


class ReverseShellObservation(ProcessObservation):

    def __init__(self, process_observation, connection_key, ssh_port):

        ProcessObservation.__init__(self, process_observation.artifact_info, process_observation.success)
        self.connection_key = connection_key
        self.ssh_port = ssh_port
