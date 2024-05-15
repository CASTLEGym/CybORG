from typing import Union

from CybORG.Shared import Observation
from CybORG.Simulator.State import State

#from CybORG.Simulator.Actions import Action


from CybORG.Emulator.Actions.Velociraptor.SSHConnectionServerAction import SSHConnectionServerAction
from CybORG.Emulator.Actions.Velociraptor.SSHConnectionClientAction import SSHConnectionClientAction
import random 
import string
from pathlib import Path
from CybORG.Emulator.Observations.Velociraptor.RemoveObservation import RemoveObservation
from CybORG.Emulator.Actions.Velociraptor.VelociraptorAction import VelociraptorAction


class RemoveAction:   
   def __init__(self, credentials_file,hostname,connection_key):
        self.credentials_file=credentials_file
        self.conn_key=connection_key
        self.hostname = hostname


   def run_command(self,command='CLOSE'): 
       ssh_connection_client_action = SSHConnectionClientAction(credentials_file=self.credentials_file,
                                              hostname=self.hostname,
                                              connection_key=self.conn_key,
                                              command=command)
       ssh_connection_client_observation = ssh_connection_client_action.execute(None)
       
       print("\n->OUTPUT from run_command =",ssh_connection_client_observation.Stdout)
       return ssh_connection_client_observation.Stdout

   def execute(self, state: Union[State, None]) -> Observation:
       out= self.run_command('rm cmd.sh && echo "Success" || echo "Failure"')
       out1=self.run_command()
       return  RemoveObservation(success=True,mal_file_removed=out,connection_removed=out1)  


if __name__=="__main__":
    credentials_file = "prog_client.yaml"
    hostname="user-host-1"

    remove_action=RemoveAction(credentials_file,connection_key,hostname)
    remove_action.execute(None)
    

