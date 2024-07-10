from CybORG.Shared import Observation


class ImpactObservation(Observation):
    def __init__(self, success,attack_id):
        super().__init__(success=success)
        self.attack_id = attack_id
