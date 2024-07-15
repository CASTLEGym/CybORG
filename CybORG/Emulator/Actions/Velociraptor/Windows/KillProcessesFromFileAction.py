from typing import Union

from CybORG.Shared import Observation
from CybORG.Simulator.State import State

from CybORG.Simulator.Actions import Action

from CybORG.Emulator.Actions.Velociraptor.GetTextFileContentsAction import GetTextFileContentsAction
from CybORG.Emulator.Actions.Velociraptor.ProcessListingAction import ProcessListingAction
from CybORG.Emulator.Actions.Velociraptor.KillProcessAction import KillProcessAction


class KillProcessesFromFileAction(Action):

    def __init__(self, credentials_file, hostname, file_path):

        super().__init__()

        self.credentials_file = credentials_file
        self.hostname = hostname
        self.file_path = file_path

    def execute(self, state: Union[State, None]) -> Observation:

        observation = Observation(False)
        get_file_contents_action = GetTextFileContentsAction(
            credentials_file=self.credentials_file, hostname=self.hostname, text_file_path=self.file_path
        )

        text_file_contents_observation = get_file_contents_action.execute(state)

        if not text_file_contents_observation.success:
            return observation

        kill_process_name_list = list(text_file_contents_observation.contents)

        process_listing_action = ProcessListingAction(
            credentials_file=self.credentials_file,
            hostname=self.hostname
        )

        process_listing_observation = process_listing_action.execute(state)

        if not process_listing_observation.success:
            return observation

        process_list = process_listing_observation.process_list

        success = True
        for process in process_list:

            for process_name in kill_process_name_list:
                if process_name in process.CommandLine:
                    kill_process_action = KillProcessAction(
                        credentials_file=self.credentials_file, hostname=self.hostname, pid=process.Pid
                    )
                    kill_process_observation = kill_process_action.execute(state)

                    if not kill_process_observation.success:
                        success = False

        observation.set_success(success)

        return observation
