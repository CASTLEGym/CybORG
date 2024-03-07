from CybORG.Shared import Observation
from CybORG.Emulator.Observations.Velociraptor.DictToAttributes import DictToAttributes


class ProcessObservation(Observation, DictToAttributes):

    def __init__(self, process_info=None, success=None):

        Observation.__init__(self, success=success)
        DictToAttributes.__init__(self, artifact_info=process_info)
