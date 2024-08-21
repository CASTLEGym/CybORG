from CybORG.Shared import Observation


class ImpactObservation(Observation):
    def __init__(self, success,attack_status=None,attack_id=None,pid=None):
        super().__init__(success=success)
        self.attack_status= attack_status
        self.attack_id = attack_id
        self.pid= pid
