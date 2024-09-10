from .ProcessObservation import ProcessObservation
from CybORG.Shared.Enums import TrinaryEnum

class MonitorObservation(ProcessObservation):

    def __init__(self, process_observation, connection_info):

        boolean_success = True if process_observation.success == TrinaryEnum.TRUE else False
        super().__init__(process_info=process_observation.artifact_info, success=boolean_success)

        self.connection_info = connection_info
