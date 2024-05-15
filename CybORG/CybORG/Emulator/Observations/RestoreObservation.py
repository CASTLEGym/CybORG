from CybORG.Shared import Observation


class RestoreObservation(Observation):

    def __init__(self, success):
        super().__init__(success=success)
