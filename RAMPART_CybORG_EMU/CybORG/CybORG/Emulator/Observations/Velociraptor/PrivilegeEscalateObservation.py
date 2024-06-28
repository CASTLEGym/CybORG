from CybORG.Shared import Observation


class PrivilegeEscalateObservation(Observation):
    def __init__(self, success,user=None,explored_host=None,pid=None):
        super().__init__(success=success)
        self.user = user
        self.explored_host= explored_host
        self.pid= pid
