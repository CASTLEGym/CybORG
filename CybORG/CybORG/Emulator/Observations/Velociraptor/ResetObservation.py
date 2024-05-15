from CybORG.Shared import Observation


class ResetObservation(Observation):

    def __init__(self, success,md5_dict):
        super().__init__(success=success)
        self.md5=md5_dict
