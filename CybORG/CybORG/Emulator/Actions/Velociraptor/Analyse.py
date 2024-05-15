from typing import Union

from CybORG.Shared import Observation
from CybORG.Simulator.State import State

from CybORG.Shared.Actions import Action

from CybORG.Emulator.Observations.Velociraptor.AnalyseObservation import AnalyseObservation

from CybORG.Emulator.Actions.Velociraptor.RunProcessAction import RunProcessAction


class AnalyseAction(Action):

    def __init__(self, credentials_file, hostname, directory, previous_verification_dict):

        super().__init__()

        self.credentials_file = credentials_file
        self.hostname = hostname
        self.directory = directory

        self.previous_verification_dict = dict(previous_verification_dict)

    def execute(self, state: Union[State, None]) -> Observation:

        md5_process_action = RunProcessAction(
            self.credentials_file,
            self.hostname,
            f"md5sum $(find \"$(realpath \"{self.directory}\")\" -maxdepth 1 -type f ! -name '.*' -exec echo \"{{}}\" +)"
        )

        md5_observation = md5_process_action.execute(None)

        if md5_observation.ReturnCode != 0:
            return Observation(False)

        current_verification_dict = {}
        md5_lines = md5_observation.Stdout.strip().splitlines()
        print('\n--> md5 checksums are:',md5_lines)
        for line in md5_lines:
            value, key = line.split()
            current_verification_dict[key] = value

        density_scout_action = RunProcessAction(
            self.credentials_file,
            self.hostname,
            f"densityscout -d \"$(realpath \"{self.directory}\")\""
        )

        density_scout_observation = density_scout_action.execute(None)

        if density_scout_observation.ReturnCode != 0:
            return Observation(False)

        density_scout_lines = density_scout_observation.Stdout.strip().splitlines()

        density_scout_dict = {}
        #print('\n-> Density scout lines are:',density_scout_lines)
        for line in density_scout_lines:
            value, key = line.split("|")
            density_scout_dict[key] = float(value)
        print('\n-> density scout dictionary:',density_scout_dict)
        analyse_observation = AnalyseObservation(
            current_verification_dict, self.previous_verification_dict, density_scout_dict
        )

        return analyse_observation
