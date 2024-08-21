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

    def execute(self, controller='lc1',attack='dos',duration=500,f_value=None) -> Observation:
       if self.conn_key== None: 
          return ImpactObservation(success=False)
       
       else: 
          if attack=='dos':
            command = f"python /home/ubuntu/OT-Sim/run_user_process.py {controller} {attack} {duration} {self.attack_id} & "
          elif attack=='fdi':
            command = f"python /home/ubuntu/OT-Sim/run_user_process.py {controller} {attack} {duration} {f_value} {self.attack_id} &"
          print('***Command:',command)
          ##to do : 
          out1= self.run_command("doas whoami")
          out=self.run_command(command)
          
          print('out is:',out, 'Its type is:',type(out))
          pid = out.split(' ')[-1]
          print('PID is:',pid)
          print('out1 is:',out1)
          return ImpactObservation(success=True, attack_status=True,attack_id=self.attack_id, pid=pid) 


    def kill_attack(self, pid) -> Observation:
       if self.conn_key== None: 
          return ImpactObservation(success=False)
       
       else: 
          #Step1: Check if PID is relevant and running
          #out1= self.run_command(f"ps -p {pid} > /dev/null && echo 1 || echo 0")
          #print("out1 from kill is:", out1, 'and its tyoe is:',type(out1))
          # If step1 is true, execute kill 
          #
          out=self.run_command(f"doas kill {pid} 2>/dev/null && echo 'True' || echo 'False'")
          print('out from kill  is:',out)
          success = out.split(' ')[-1]
          print('success is:',success,'its type is ', type(success))
          if success=='True\n':
           print('In true ....')
           return ImpactObservation(success=True, attack_status= False, attack_id=None, pid=None) 
          else: 
           return ImpactObservation(success=False)
