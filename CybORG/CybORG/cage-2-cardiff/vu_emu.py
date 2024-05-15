# main is to run the game coordinator and control entire emulation.
import numpy as np
import os
# from vu_emu import vu_emu
import random
import importlib.util
import sys
import subprocess
import yaml
import time
from CybORG.Agents.Wrappers.BaseWrapper import BaseWrapper
from CybORG.Agents.Wrappers.TrueTableWrapper import TrueTableWrapper
from utils import *
from ipaddress import IPv4Network, IPv4Address
import ast
from CybORG.Emulator.Actions.Velociraptor.ResetAction import ResetAction
from CybORG.Emulator.Actions.Velociraptor.DiscoverNetworkServicesAction import DiscoverNetworkServicesAction
from CybORG.Emulator.Actions.Velociraptor.DiscoverRemoteSystemsAction import DiscoverRemoteSystemsAction
from CybORG.Emulator.Actions.Velociraptor.ExploitAction import ExploitAction
from CybORG.Emulator.Actions.Velociraptor.PrivilegeEscalateAction import PrivilegeEscalateAction
#from CybORG.Emulator.Actions.SshAction import SshAction
from CybORG.Emulator.Actions.DecoyAction import DecoyAction
from CybORG.Emulator.Actions.Velociraptor.AnalyseAction import AnalyseAction
from CybORG.Emulator.Actions.Velociraptor.RemoveAction import RemoveAction
from pprint import pprint
import ast

file_path = './assets/mod_100steps_cardiff_bline.py'
machine_config_path='./assets/machine_configs/'
#c2o= cage2_os()
import re
import json

#from CybORG.Emulator.Velociraptor.Actions.RunProcessAction import RunProcessAction

ip2host= name_conversion("./assets/openstack_ip_map.json")
cage2os=name_conversion("./assets/cage2-openstack.yaml")

credentials_file = "/home/ubuntu/agent_client.yaml"
#credentials_file = "prog_client2.yaml"


blue_action_space= ['DecoyApache', 'DecoySSHD', 'DecoyVsftpd', 'Restore', 'DecoyFemitter', 'Remove', 'DecoyTomcat', 'DecoyHarakaSMPT']
blue_decoys=['DecoyApache', 'DecoySSHD', 'DecoyVsftpd', 'DecoyTomcat', 'DecoyFemitter','DecoyHarakaSMPT'] # windows specific decoys are faked. 
red_action_space = ['PrivilegeEscalate', 'ExploitRemoteService', 'DiscoverRemoteSystems', 'DiscoverNetworkServices']
vms=["User0","User1","User2","User3","User4","Enterprise0","Enterprise1","Enterprise2","Op_Host0","Op_Host1","Op_Host2","Op_Server0","Defender"]
red_info={"User0"}
blue_info={}
#Store action and resultant result (True/False) 
blue_actions=[]
red_actions=[]
counter=0


service_ports = {
    'Apache': 80,
    'SSHD': 22,
    'Vsftpd': 21,
    'Femitter':21,
    'Tomcat': 443,
    'HarakaSMPT': 25
}

print(service_ports)



utils=utils()
print(dir(utils))


from enum import Enum

class TrinaryEnum(Enum):
    TRUE = 1
    FALSE = 0
    UNKNOWN = -1

def enum_to_boolean(enum_value):
    if enum_value == 'TRUE':
        return True
    elif enum_value == 'FALSE':
        return False
    else:
        return None


class vu_emu():
   def __init__(self):
      self.old_outcome_blue=None
      self.old_outcome_red=None
      self.last_red_action=None
      self.last_red_action_param=None
      self.connection_key={}
      
   def reset(self):
       
       with open('./assets/blue_baseline_obs.py','r') as f:
         baseline= json.load(f)
       self.baseline= ast.literal_eval(baseline)
       print('Self baseline type is:',type(self.baseline))
       """
       self.baseline={}
       for vm in vms:
          #curr_dir=os.getcwd()
          #host_dir= os.path.join('./machines/', vm)
          #print('Host dir is:',host_dir)
          self.baseline[vm]=self.get_machine_intial_state(vm)
       
       reset=ResetAction(credentials_file)
       self.md5={}
       for vm in vms:
          #curr_dir=os.getcwd()
          #host_dir= os.path.join('./machines/', vm)
          os_vm=cage2os.fetch_alt_name(vm)
          obs=reset.execute(os_vm)
          if obs.success==True: 
              self.md5[vm]=obs.md5
          else: 
              print('Reset failed!!')
              break
       print("baseline estimated by US  is:")
       pprint(self.baseline)
       print("md5 are:",self.md5)
       time.sleep(30)  
       """
       return None, None
       
   def get_action_space(self,agent="Red"):
       return None, None

   
   def step(self,action_string,agent_type):
       ("In steps")
       split_action_string=action_string.split(" ")
       
       #if action contains the hostname
       if len(split_action_string)==2:
         action_param= split_action_string[1]
         action_name=split_action_string[0]
         
         #print("\n in vu_emu=> Action name:",action_name,";action parameter is:",action_param)
         is_host_name= self.is_name(action_param)
         if is_host_name == True:
            print("** True host name **") 
            action_param= ip2host.fetch_alt_name(action_param)
            print("=> Action param is",action_param)
            
         if agent_type=='red':
            outcome= self.execute_action_client(action_name,action_param)
            outcome= self.transfrom_observation(action_name,outcome)
            print('--> transformed outcome is:', outcome)
            self.old_outcome_red=outcome
            self.last_red_action=action_name
            self.last_red_action_param=action_param
            #print('obs is:',outcome)
         
         elif agent_type=='blue':
          if action_name in blue_action_space :
            #  ->>> Execute locally
            #outcome=self.execute_action_locally(action_name,action_param)
            
            #  ->> Execute on client
            outcome= self.execute_action_client(action_name,action_param)
            outcome= self.transfrom_observation(action_name,outcome)
            #modify blue only if red is taking following actions:
            #red_actions_that_affect_blue= ['PrivilegeEscalate', 'ExploitRemoteService', 'DiscoverNetworkServices']
            #if action_name in red_actions_that_affect_blue: 
            #   outcome=modify_blue_by_red(outcome,self.old_outcome_red,self.last_red_action,self.last_red_action_param)
            
            #print("Outcome is:",outcome)
            #  ->>> Execute on client
            #outcome= execute_action_client(action_name,open_stack_host_name)
          else: 
            print("Invalid action!!")
            sys.exit(1)
          self.old_outcome_blue=outcome
       #if action doesnot contains the hostname (like sleep/monitor) 
       else: 
          if action_name=='Sleep':
               outcome={'success': 'Unknown'}
          else:
              print('!!! Not Implemented !!!')
              
       return outcome, None, None, None

   def execute_action_client(self,action_name,action_param,running_from=None):
       print('@'*80, '\n ==>action name is:',action_name, 'action_params is:',action_param)

       ### Red Actions
       if action_name=='DiscoverRemoteSystems': 
          action=DiscoverRemoteSystemsAction(credentials_file,'user-host-1',action_param)
          observation=action.execute(None)
          success = enum_to_boolean(str(observation.success))
          #print('observation success is:',observation.success,'transformed success is:',success)
          outcome={}

          outcome.update({'success':success})

          ip_list= observation.ip_address_list
          filtered_list = [ip for ip in ip_list if not ip.endswith('.5') and not ip.endswith('.251')]
          print(filtered_list)
          outcome.update({action_param:filtered_list})
          print('\n-> outcome of DiscoverRemoteSystem is:',outcome)
       elif action_name=='DiscoverNetworkServices': 
          action=DiscoverNetworkServicesAction(credentials_file,'user-host-1',action_param)
          observation=action.execute(None)

          success = enum_to_boolean(str(observation.success))
          outcome={}
          outcome.update({'success':success})
          outcome.update({action_param:observation.port_list})
          print('\n->outcome of DiscoverNetworkServices is:',outcome)

       elif action_name=='ExploitRemoteService':
          action= ExploitAction(credentials_file,'user-host-1',action_param,'vagrant','vagrant',4444)
          observation=action.execute(None)

          success = enum_to_boolean(str(observation.success))
          outcome={}
          outcome.update({'success':success})
          outcome.update({'host_ip':action_param})
          outcome.update({'available_exploit':observation.available_exploit})
          outcome.update({'ip_info':observation.ip_address_info})
          self.connection_key.update({ip2host.fetch_alt_name(action_param):observation.connection_key})
          print('Connection keys are:',self.connection_key)
          print('\n->outcome of Exploit action is:',outcome)

       elif action_name=='PrivilegeEscalate':
          action= PrivilegeEscalateAction(credentials_file,'user-host-1',action_param,'vagrant','vagrant',4444)
          observation=action.execute(None)
          
          success = enum_to_boolean(str(observation.success))
          outcome={}
          outcome.update({'success':success})
          outcome.update({'action_param':action_param})
          outcome.update({'user':observation.user})
          outcome.update({'explored_host':observation.explored_host})
          outcome.update({'pid_string':observation.pid})
          print('\n->outcome of Exploit action is:',outcome)

       ### Blue Actions
       elif action_name in blue_decoys: 
          print('In decoy, action name is:',action_name,'param is:',action_param)
          decoyname= action_name[5:] 
          decoyport= service_ports[decoyname]
          username='ubuntu'
          deploy_decoy = DecoyAction(action_param, username, 'ubuntu', decoyname, decoyport)
          observation = deploy_decoy.execute(None)
          success = enum_to_boolean(str(observation.success))
          outcome={}
          outcome.update({'success':success})
          outcome.update({'host':ip2host.fetch_alt_name(action_param)})
          outcome.update({'decoyname':decoyname})
          outcome.update({'username':username})
          print('\n->outcome of Decoy is:',outcome)

       elif action_name=='Remove': 
          remove_action = RemoveAction(credentials_file,action_param,self.connection_key[action_param])
          observation=remove_action.execute(None)
          outcome={observation.success}
          #to do : delete the connection key

       elif action_name=='Restore':
          restore_action = RestoreAction(hostname=action_param,
          auth_url='https://cloud.isislab.vanderbilt.edu:5000/v3',
          project_name='mvp1',
          username='xyz',
          password='******',
          user_domain_name='ISIS',
          project_domain_name='ISIS')
          
          restore_action.execute(None)



       elif action_name=='Analyze':
          
          outcome= {'success':False}
       elif action_name=='Sleep':
          outcome= {'success':True}
       print('--> Outcome of action is:',outcome)
       return outcome

   def transfrom_observation(self,action_name,data):
       if action_name=='DiscoverRemoteSystems':
         return utils.transform_DiscoverRemoteSystems(data)    
       elif action_name=='DiscoverNetworkServices':
         return utils.transform_DiscoverNetworkServices(data)  
       elif action_name=='ExploitRemoteService':
         return utils.transform_ExploitRemoteService(data) 
       elif action_name=='PrivilegeEscalate':
         return utils.transform_PrivilegeEscalate(data)  
       elif action_name in blue_decoys:
         return utils.transform_decoy(data)   

   def execute_action_locally(self,action_name,action_param,running_from=None):
            parameters = [action_name , action_param]
            server_directory = os.getcwd()
            # Get one level up
            #one_level_up = os.path.dirname(server_directory)
            # Get two levels up
            #two_levels_up = os.path.dirname(one_level_up)
            #print("Original Directory:", original_directory)
            
            #print('action param is:',action_param)
            #Specify the subfolder you want to change to
            if running_from!= None:
               subfolder = running_from
            else:
               subfolder=action_param
            # Join the original directory with the subfolder
            new_directory = os.path.join('./machines/')
            # Change to the subfolder
            os.chdir(new_directory)
            print("Current Working Directory (after changing to subfolder):", os.getcwd())
            
            # Specify the Python script to execute
            script_path = './action_executor.py'
            try:
              # Run the Python script and capture its output
              print(['python', script_path]+parameters)
              #result = subprocess.check_output(['python', script_path]+parameters, universal_newlines=True, stderr=subprocess.STDOUT)
              result =subprocess.run(['python', script_path]+parameters, capture_output=True, text=True, check=True)
              # Print the captured output
              print("*** Output of the script ***:",result)

              
            except subprocess.CalledProcessError as e:
              # Handle if the subprocess returns a non-zero exit code
              #print("*** Output of the script ***:",result.stderr)
              print(f"Error: {e}")
            # Change back to the original directory
            os.chdir(server_directory)
            #print("Current Working Directory (after coming back to the original):", os.getcwd())
            #print("\n \n")
            #return result.stdout
            return ast.literal_eval(result.stdout)
            
   def is_name(self,s):
         return bool(re.match(r"^[A-Za-z]+", s))
   
   
   def parse_blue_outcome(self,outcome):
       print("In parse blue, outcome is:",outcome)
       return outcome
       
   def parse_red_outcome(self,outcome):
       
       print("In parse red, outcome is:",outcome)
       return outcome   
   
   def get_machine_intial_state(self,path):
     file_path= './machines/config_'+path+'.yaml'
     #print('file path is:',file_path)
     try:
       with open(file_path, 'r') as file:
            data = yaml.safe_load(file)
            pids = [process["PID"] for process in data["Test_Host"]["Processes"]]
            formatted_pid = {'Processes':[{'pid': pid} for pid in pids]}
     except FileNotFoundError:
      # If the file doesn't exist, create an empty data structure.
      print('No file found error !!')  
     return formatted_pid
           
   
