from .ProcessObservation import ProcessObservation


class SSHConnectionServerObservation(ProcessObservation):

    def __init__(self, process_observation, connection_key):

        ProcessObservation.__init__(self, process_observation.artifact_info, process_observation.success)
        self.connection_key = connection_key
