from typing import Union

from xml.etree import ElementTree
import time
from .RunProcessAction import RunProcessAction
from CybORG.Shared import Observation
from CybORG.Simulator.State import State
from ...Observations.Velociraptor.MonitorObservation import MonitorObservation
#from CybORG.Emulator.Observations.Velociraptor.MonitorObservation import MonitorObservation

class MonitorAction(RunProcessAction):

    def __init__(self, credentials_file, hostname):
        self.last_timestamp= int(time.time())
        print("Current Unix time:", self.last_timestamp)
        
        # Define the path to your Zeek log file
        self.LOG_FILE = "/usr/local/zeek/logs/current/conn.log"

        super().__init__(
            credentials_file=credentials_file,
            hostname=hostname, 
            command = f"cat {self.LOG_FILE}"
            )



    def execute(self, state: Union[State, None]) -> Observation:

        observation = super().execute(state)
        self.last_timestamp= int(time.time())

        print('observation dict:',observation.__dict__)
        print('Stdout is:',observation.Stdout)
        if observation.success== True:
          observation.set_success(True)
          return MonitorObservation(observation,observation.Stdout)
        
        observation.set_success(False)
        