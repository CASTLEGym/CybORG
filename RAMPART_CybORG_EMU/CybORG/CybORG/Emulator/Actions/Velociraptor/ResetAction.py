from typing import Union

from xml.etree import ElementTree

from .RunProcessAction import RunProcessAction
from CybORG.Shared import Observation
from CybORG.Simulator.State import State
from ...Observations.Velociraptor.ResetObservation import ResetObservation

from CybORG.Shared.Actions import Action


class ResetAction(Action):

    def __init__(self, credentials_file):
        super().__init__()
        self.credentials_file = credentials_file
        self.directory = None

    def execute(self, hostname= None,directory='/home/ubuntu', state: Union[State, None]=None) -> Observation:
        self.directory=directory
        self.hostname=hostname
        print("In execute")
        md5_process_action = RunProcessAction(
            self.credentials_file,
            self.hostname,
            f"md5sum $(find \"$(realpath \"{self.directory}\")\" -maxdepth 1 -type f -exec echo \"{{}}\" +)"
        )
        md5_observation = md5_process_action.execute(None)
        
        print('md5 observation is :',md5_observation.__dict__)
        if hasattr(md5_observation, 'ReturnCode'):
          if md5_observation.ReturnCode != 0:
            return Observation(False)
          else:
            current_verification_dict = {}
            md5_lines = md5_observation.Stdout.strip().splitlines()
            print('\n--> md5 checksums are:',md5_lines)
            for line in md5_lines:
              value, key = line.split()
              current_verification_dict[key] = value

            return ResetObservation(True,current_verification_dict)
