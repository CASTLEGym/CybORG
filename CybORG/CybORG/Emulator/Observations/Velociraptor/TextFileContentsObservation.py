from CybORG.Emulator.Observations.Velociraptor.ProcessObservation import ProcessObservation


class TextFileContentsObservation(ProcessObservation):

    def __init__(self, process_observation):

        self.Stdout = ""  # So IDE doesn't complain about assignment below

        super().__init__(process_info=process_observation.artifact_info)

        self.contents = self.Stdout.splitlines()
