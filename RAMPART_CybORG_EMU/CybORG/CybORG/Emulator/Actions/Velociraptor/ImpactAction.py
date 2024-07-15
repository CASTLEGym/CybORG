from typing import Union
from CybORG.Shared import Observation
from CybORG.Simulator.State import State
from CybORG.Emulator.Actions.Velociraptor.SSHConnectionImpactAction import SSHConnectionImpactAction
from CybORG.Emulator.Observations.Velociraptor.ImpactObservation import ImpactObservation
import random
import string
class ImpactAction: 
    
    connection_key_size = 4
    
    @classmethod
    def get_attack_id(cls):
        return ''.join(
            random.SystemRandom().choice(
                string.ascii_uppercase + string.digits
            ) for _ in range(cls.connection_key_size)
        )

    def __init__(self, credentials_file,hostname, connection_key=None):
        self.credentials_file=credentials_file
        self.conn_key=connection_key
        self.hostname = hostname
        self.attack_id=self.get_attack_id()
    
     

    def run_command(self,command='ps aux'):
       ssh_connection_client_action = SSHConnectionImpactAction(
           credentials_file=self.credentials_file,
           hostname=self.hostname,
           connection_key=self.conn_key,
           command=command
       )
       ssh_connection_client_observation = ssh_connection_client_action.execute(None)
       return ssh_connection_client_observation.Stdout

    def execute(self, controller='lc1',attack='dos',duration=200,f_value=None) -> Observation:
       if self.conn_key== None: 
          return ImpactObservation(success=False)
       else: 
          if attack=='dos':
            command = f"python /home/ubuntu/Git/OT-Networks/run_user_process.py {controller} {attack} {duration} {self.attack_id} &"
          elif attack=='fdi':
            command = f"python /home/ubuntu/Git/OT-Networks/run_user_process.py {controller} {attack} {duration} {f_value} {self.attack_id} &"
          print('***Command:',command)
          ##to do : 
          out=self.run_command(command)
          print('out is:',out)
          return ImpactObservation(success=True, attack_id=self.attack_id,stdout=out) 


if __name__=="__main__":
    credentials_file = "/home/ubuntu/prog_client.yaml"
    hostname = "user0"
    remote_hostname = "10.10.30.20"
    remote_username = "ubuntu"
    remote_password = "ubuntu"
    client_port = 4444

    pes_action=PrivilegeEscalateAction(
        credentials_file, connection_key, hostname, remote_hostname, remote_username, remote_password, client_port
    )
   
    observation= pes_action.execute(None)
    print(observation.user,observation.explored_host,observation.pid)
    print('Please clean the mess by killing the SSHConnectionServer.py/SSHConnectionServerClient.py')

