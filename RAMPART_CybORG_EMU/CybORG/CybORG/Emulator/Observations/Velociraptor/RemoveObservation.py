from CybORG.Shared import Observation


class RemoveObservation(Observation):

    def __init__(self, success='Unknown',mal_file_removed=None,connection_removed=None):
        super().__init__(success=success)
        self.malicious_file_removed=mal_file_removed
        self.connection_removed= connection_removed
