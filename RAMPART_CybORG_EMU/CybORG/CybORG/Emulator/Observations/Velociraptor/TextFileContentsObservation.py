from CybORG.Emulator.Observations.Velociraptor.ProcessObservation import ProcessObservation
from CybORG.Shared.Enums import TrinaryEnum


class TextFileContentsObservation(ProcessObservation):

    def __init__(self, process_observation):

        self.Stdout = ""  # So IDE doesn't complain about assignment below

        boolean_success = True if process_observation.success == TrinaryEnum.TRUE else False
        super().__init__(process_info=process_observation.artifact_info, success=boolean_success)

        self.contents = self.Stdout.splitlines()
