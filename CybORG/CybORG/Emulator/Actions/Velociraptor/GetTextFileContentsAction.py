from typing import Union

from CybORG.Shared import Observation
from CybORG.Simulator.State import State

from CybORG.Emulator.Actions.Velociraptor.RunProcessAction import RunProcessAction
from CybORG.Emulator.Observations.Velociraptor.TextFileContentsObservation import TextFileContentsObservation


class GetTextFileContentsAction(RunProcessAction):

    def __init__(self, credentials_file, hostname, text_file_path):

        super().__init__(
            credentials_file=credentials_file,
            hostname=hostname,
            command=f"cat {text_file_path}"
        )

    def execute(self, state: Union[State, None]) -> Observation:

        return TextFileContentsObservation(super().execute(state))
