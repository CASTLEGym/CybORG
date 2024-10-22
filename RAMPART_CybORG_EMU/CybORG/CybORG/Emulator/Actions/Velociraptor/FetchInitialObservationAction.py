from typing import Union

from CybORG.Shared import Observation
from CybORG.Simulator.State import State

from CybORG.Shared.Actions import Action

from CybORG.Emulator.Actions.Velociraptor.RunProcessAction import RunProcessAction

#python /usr/local/scripts/python/fetch_host_detailed_info.py

class FetchInitialObservationAction(Action):
    def __init__(self, credentials_file):
        super().__init__()
        self.credentials_file = credentials_file
        
    def execute(self, hostname=None) -> Observation:
        print('host is:',hostname)
        self.hostname=hostname
        fetch_action = RunProcessAction(
            self.credentials_file,
            self.hostname,
            f"python /usr/local/scripts/python/fetch_host_detailed_info.py"
        )

        fetch_observation = fetch_action.execute(None)
        print('Fetch observation:',fetch_observation)

        if fetch_observation.ReturnCode != 0:
            return Observation(False)

        return fetch_observation
