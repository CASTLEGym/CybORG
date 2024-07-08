from typing import Union
from CybORG.Shared import Observation
from CybORG.Simulator.State import State
from CybORG.Emulator.Actions.Velociraptor.SSHConnectionImpactAction import SSHConnectionImpactAction
from CybORG.Emulator.Observations.Velociraptor.PrivilegeEscalateObservation import PrivilegeEscalateObservation

class PrivilegeEscalateAction: 
  
    def __init__(self, credentials_file,hostname, connection_key=None, remote_host_name=None,remote_username=None, remote_password=None,client_port=None):
        self.credentials_file=credentials_file
        self.conn_key=connection_key
        self.hostname = hostname
        self.remote_hostname=remote_host_name
        self.remote_username=remote_username
        self.remote_password=remote_password
        self.client_port= client_port

    def run_command(self,command='CLOSE'):
       ssh_connection_client_action = SSHConnectionImpactAction(
           credentials_file=self.credentials_file,
           hostname=self.hostname,
           connection_key=self.conn_key,
           command=command
       )
       ssh_connection_client_observation = ssh_connection_client_action.execute(None)
       return ssh_connection_client_observation.Stdout

    def execute(self, state: Union[State, None]) -> Observation:
       if self.conn_key== None: 
          return PrivilegeEscalateObservation(success=False)
       else: 
          command = f"sudo ss -tunap | grep ':{self.client_port}'"
          out1=self.run_command("sudo whoami")
          out2=self.run_command("grep -oE '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' ~/.ssh/known_hosts")
          out3=self.run_command(command)
          return PrivilegeEscalateObservation(success=True,user=out1,explored_host=out2,pid=out3) 


if __name__=="__main__":
    credentials_file = "/home/ubuntu/prog_client.yaml"
    hostname = "user0"
    remote_hostname = "10.10.10.13"
    remote_username = "vagrant"
    remote_password = "vagrant"
    client_port = 4444

    pes_action=PrivilegeEscalateAction(
        credentials_file, connection_key, hostname, remote_hostname, remote_username, remote_password, client_port
    )
   
    observation= pes_action.execute(None)
    print(observation.user,observation.explored_host,observation.pid)
    print('Please clean the mess by killing the SSHConnectionServer.py/SSHConnectionServerClient.py')

