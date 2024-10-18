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
import inspect
from CybORG import CybORG
from CybORG.Agents.Wrappers.BaseWrapper import BaseWrapper
from CybORG.Agents.Wrappers.TrueTableWrapper import TrueTableWrapper
from utils import *
from env_utils import *
from ipaddress import IPv4Network, IPv4Address
import ast
from CybORG.Emulator.Actions.RestoreAction import RestoreAction
from CybORG.Emulator.Actions.Velociraptor.ResetAction import ResetAction
from CybORG.Emulator.Actions.Velociraptor.DiscoverNetworkServicesAction import DiscoverNetworkServicesAction
from CybORG.Emulator.Actions.Velociraptor.DiscoverRemoteSystemsAction import DiscoverRemoteSystemsAction
from CybORG.Emulator.Actions.Velociraptor.ExploitAction import ExploitAction
from CybORG.Emulator.Actions.Velociraptor.PrivilegeEscalateAction import PrivilegeEscalateAction
#from CybORG.Emulator.Actions.SshAction import SshAction
from CybORG.Emulator.Actions.DecoyAction import DecoyAction
from CybORG.Emulator.Actions.Velociraptor.AnalyseAction import AnalyseAction
from CybORG.Emulator.Actions.Velociraptor.RemoveAction import RemoveAction
from CybORG.Emulator.Actions.Velociraptor.SSHConnectionImpactAction import SSHConnectionImpactAction
from reward_calculator import RewardCalculator
#from pprint import pprint
import ast
import json
from reward_calculator import RewardCalculator

from CybORG.Agents import B_lineAgent, SleepAgent
from Wrappers.ChallengeWrapper2 import ChallengeWrapper2
from Wrappers.BlueEmulationWrapper import BlueEmulationWrapper

file_path = './assets/mod_100steps_cardiff_bline.py'
machine_config_path='./assets/machine_configs/'
#c2o= cage2_os()
import re
import json
import ast

#from CybORG.Emulator.Velociraptor.Actions.RunProcessAction import RunProcessAction

ip2host= name_conversion("./assets/openstack_ip_map.json")
cage2os=name_conversion("./assets/cage2-openstack.yaml")

cage2os_instance=name_conversion("./assets/cage2-openstack_instance.yaml")

credentials_file = "/home/ubuntu/prog_client.yaml"
#credentials_file = "prog_client2.yaml"


blue_action_space= ['DecoyApache', 'DecoySSHD', 'DecoyVsftpd', 'Restore', 'DecoyFemitter', 'Remove', 'DecoyTomcat', 'DecoyHarakaSMPT','Analyse']
blue_decoys=['DecoyApache', 'DecoySSHD', 'DecoyVsftpd', 'DecoyTomcat', 'DecoyFemitter','DecoyHarakaSMPT'] # windows specific decoys are faked. 
red_action_space = ['PrivilegeEscalate', 'ExploitRemoteService', 'DiscoverRemoteSystems', 'DiscoverNetworkServices']
vms=["User0","User1","User2","User3","User4","Enterprise0","Enterprise1","Enterprise2","Op_Host0","Op_Host1","Op_Host2","Op_Server0","Defender"]
red_info={"User0"}
blue_info={}
#Store action and resultant result (True/False) 
blue_actions=[]
red_actions=[]
counter=0
modify_blue_red=True
red_intial_foothold='user0'


service_ports = {
    'Apache': 80,
    'SSHD': 22,
    'Vsftpd': 21,
    'Femitter':21,
    'Tomcat': 443,
    'HarakaSMPT': 25
}

#print(service_ports)

scenario = 'Scenario2'
path = str(inspect.getfile(CybORG))
print("path is:",path)
path = path[:-10] + f'/Shared/Scenarios/{scenario}.yaml'
print('path is:',path)


utils=utils()
#print(dir(utils))
#env_utils= env_utils()
#print(dir(env_utils))


class setup_openstack:
   # should be called by another function before emulation class is called. emulation uses the attributes
   def __init__(self, current_user,password,url,udn,pdn,project,key_name):
      self.current_user= current_user
      self.password= password
      self.url=url
      self.udn=udn
      self.pdn=pdn
      self.project=project
      self.key_name= key_name

class rampart_emulator():
   def __init__(self, game_param):
      # Parse the Json string into a Python dictionary
      print('In Rampart emulator',game_param)

      # If game_param is already a dictionary, use it as-is
      if isinstance(game_param, dict):
        config_dict = game_param
      else:
        # Otherwise, assume it's a JSON string and parse it
        config_dict = json.loads(game_param)


      if validate_game_param(config_dict):
        # Store values in variables
        self.scenario = config_dict.get('scenario')
        self.main_agent = config_dict.get('main_agent')
        self.blue_agent = config_dict.get('blue_agent')
        self.red_agent = config_dict.get('red_agent')
        self.wrapper = config_dict.get('wrapper')
        self.episode_length= config_dict.get('episode_length')
        self.max_episodes= config_dict.get('max_episodes')
      
        # Optional: Print only for testing
        print(f"Scenario: {self.scenario}")
        print(f"Main Agent: {self.main_agent}")
        print(f"Blue Agent: {self.blue_agent}")
        print(f"Red Agent: {self.red_agent}")
        print(f"Wrapper: {self.wrapper}")
      
      if self.red_agent!= None:
        self.red_agent= globals()[self.red_agent]
      
      self.old_outcome_blue=None
      self.old_outcome_red=None
      self.last_red_action=None
      self.last_red_action_param=None
      self.connection_key={}
      self.available_ports=generate_ports()
      #print('\n-> Available port:',self.available_ports)
      self.used_ports={}
      self.exploited_hosts=[]
      self.priviledged_hosts=[]
      self.old_exploit_outcome={}
      self.network_state={}
      self.terminated= False
      self.done= False
      self.step_counter=0
      self.reward_cal=RewardCalculator(path)
      

      with open("./assets/openstack_ip_map.json",'r') as f:
         self.os_ip_data = yaml.safe_load(f)
      #print('Data is:',self.data)
      

      # Intialising openstack specific 
      self.openstack_setup= setup_openstack(current_user= 'vardhah',
                                              password= 'Roadies@5*',
                                              url="https://cloud.isislab.vanderbilt.edu:5000/v3",
                                              udn="ISIS",
                                              pdn="ISIS",
                                              project="castle3",
                                              key_name= "castle-control")
      

   
   def intialize_game_related_data(self):
      cyborg = CybORG(path, 'sim', agents={'Red': self.red_agent})
      wrapped_cyborg = wrap(cyborg,"cardiff")    # Hardcoding to 'cardiff' to just extract intial data from my version of Cyborg.  
      #reward_calc.reset()
      #this intialisation information is coming from Cyborg
      blue_observation = wrapped_cyborg.reset()      
      blue_action_space = wrapped_cyborg.get_action_space(self.main_agent)

      blue_observation=cyborg.get_observation('Blue')
      blue_action_space= cyborg.get_action_space('Blue')
      print('Blue observation:',blue_observation)
      print('blue_action_space:',blue_action_space)

      # Getting intial red_observation
      red_observation=cyborg.get_observation('Red')
      red_action_space= cyborg.get_action_space('Red')
      red_observation=translate_intial_red_obs(red_observation)
      print("\n ***** Red observation after reset is:",red_observation)
      print("\n ***** Red action space after reset is:",red_action_space)
    
      #read assets
      blue_action_list=load_data_from_file('./assets/blue_enum_action.txt')
      with open('./assets/blue_initial_obs.json', 'r') as file:
        initial_blue_info = json.load(file)
      initial_blue_info= translate_initial_blue_info(initial_blue_info)
      # print('\n blue action list:',blue_action_list)
      # print('\n\n->  Blue info after reset, in game coordinator::',initial_blue_info)
      #parse_and_store_ips_host_map(initial_blue_obs)
      if self.wrapper=='ChallengeWrapper':
        emu_wrapper=BlueEmulationWrapper(cyborg_emu.baseline)
        # Translate intial obs in vectorised format to feed into NN
        blue_observation=emu_wrapper.reset(initial_blue_info)
      return blue_action_list,blue_observation
   
   def reset(self,seed=None,agent=None ):
      if seed is not None and not isinstance(seed, int):
        raise TypeError("Parameter 'seed' must be of type 'int' or 'None'.")
      # Check if agent is either None or a string
      if agent is not None and not isinstance(agent, str):
        raise TypeError("Parameter 'agent' must be of type 'str' or 'None'.")

      action_list,observation=self.intialize_game_related_data()
      print('action list is:',action_list)
      print('Observation is:',observation)
      with open('./assets/blue_baseline_obs.py','r') as f:
        baseline= json.load(f)
      self.baseline= ast.literal_eval(baseline)
      #print('Self baseline type is:',type(self.baseline))
       
      self.baseline={}
      for vm in vms:
          self.baseline[vm]=self.get_machine_intial_state(vm)
       
      reset=ResetAction(credentials_file)
      self.md5={}
      for vm in vms: 
        os_vm=cage2os.fetch_alt_name(vm)
        print('--> VM is:',vm, 'os name is:',os_vm)
        obs=reset.execute(os_vm)

        if obs.success==True: 
          self.md5[ip2host.fetch_alt_name(vm)]=obs.md5
        else: 
          print('Reset failed!!')
          self.md5[ip2host.fetch_alt_name(vm)]=None
          # if md5 fails due to grpc issue , just returning None. Need to ponder how to manage it. 
          #break
          
      print("baseline estimated by us is:")
      #pprint(self.baseline)
      print("md5 are:",self.md5)
      #time.sleep(30)   
      return action_list, observation
       
   def get_action_space(self,agent="Red"):
       return None, None

   def update_reward_information_dict(self,info_dict, server_name, username):
    if server_name not in info_dict:
        info_dict[server_name] = {'Sessions': []}
    info_dict[server_name]['Sessions'].append({'Username': username})
   
   def delete_reward_information_dict(self,info_dict, server_name, username):
    if server_name in info_dict:
        sessions = info_dict[server_name]['Sessions']
        info_dict[server_name]['Sessions'] = [session for session in sessions if session['Username'] != username]
        
        # If there are no more sessions, remove the server entry
        if not info_dict[server_name]['Sessions']:
            del info_dict[server_name]
    return info_dict


   
   def step(self,action_string: str,agent_type: str):
       if not isinstance(action_string, str) or not isinstance(agent_type, str):
            raise TypeError("Both parameters must be of type 'str'.")
       
       ("In steps")
       split_action_string=action_string.split(" ")
       
       #if action contains the hostname
       if len(split_action_string)==2:
         action_param= split_action_string[1]
         action_name=split_action_string[0]
         
         #print("\n in vu_emu=> Action name:",action_name,";action parameter is:",action_param)
         is_host_name= self.is_name(action_param)
         if is_host_name == True:
            #print("** True host name **") 
            action_param= ip2host.fetch_alt_name(action_param)
            #print("\n=>Blue action:: Action name -",action_name, '; action param-',action_param)
            
         if agent_type=='Red':
            outcome= self.execute_action_client(action_name,action_param)
            outcome= self.transfrom_observation(action_name,outcome)
            print('--> transformed outcome is:', outcome)
            self.old_outcome_red=outcome
            self.last_red_action=action_name
            self.last_red_action_param=action_param
            #print('obs is:',outcome)
         
         elif agent_type=='Blue':
          if action_name in blue_action_space :
            #  ->>> Execute 
            outcome= self.execute_action_client(action_name,action_param)
            # Transform the emulator outcome in Cyborg observation
            outcome= self.transfrom_observation(action_name,outcome)
            if modify_blue_red==True: 
             #print('###'*100,self.last_red_action)
             #modify blue only if red is taking following actions:
             red_actions_that_affect_blue= ['ExploitRemoteService', 'DiscoverNetworkServices']
             if self.last_red_action in red_actions_that_affect_blue:
                #print('In modify') 
                outcome=self.modify_blue_by_red(outcome,self.old_outcome_red,self.last_red_action,self.last_red_action_param) 
                #print("Outcome is:",outcome)
          else: 
            print("Invalid action!!")
            sys.exit(1)
          self.old_outcome_blue=outcome
       #if action doesnot contains the hostname (like sleep/monitor) 
       else: 
          #print('In else:',action_string)
          if action_string=='Sleep':
               outcome={'success': 'Unknown'}
          else:
              print('!!! Not Implemented !!!')  
       self.step_counter+=1
       if self.step_counter==self.episode_length:
          self.done= True 
       reward=self.reward_cal.reward(self.network_state)    
       return outcome, reward, None, self.done
   
   def close(self):
       return 0

   def modify_blue_by_red(self,blue_outcome,red_outcome,last_red_action,last_red_action_param):
      #print('@@@@@'*100)
      print('-> Blue outcome:',blue_outcome)
      if last_red_action=='DiscoverNetworkServices':
        for key,value in red_outcome.items():
          if self.fetch_ip(key)!= None: 
              red_data=red_outcome[key]
              host=ip2host.fetch_alt_name(key)
              blue_outcome.update({host:red_data})
      elif last_red_action=='ExploitRemoteService':
        #print('%%%%'*100,'In modify of exploit',)
        red_data= red_outcome[last_red_action_param]
        #print('red data in exploit is:',red_data)
        if red_outcome['success']==True:
          red_to_blue=self.convert_red_exploit_dict(red_data)
        elif red_outcome['success']==False:
          # Iterate over all the processes and their connections
          red_to_blue = {'Processes': []}
          for process in red_data['Processes']:
            for connection in process['Connections']:
              new_connection1 = {
                'local_port': connection['local_port'],
                'remote_port': 53259,  # Assuming remote_port is a fixed value
                'local_address': connection['local_address'],
                'remote_address': IPv4Address('10.0.214.186')}
            
              new_connection2 = {
                'local_port': connection['local_port'],
                'local_address': connection['local_address'],
                'remote_address': IPv4Address('10.0.214.186')}
            
              red_to_blue['Processes'].append({'Connections': [new_connection1]})
              red_to_blue['Processes'].append({'Connections': [new_connection2]})
        attacked_hostname=ip2host.fetch_alt_name(last_red_action_param)
        blue_outcome.update({attacked_hostname:red_to_blue})
      return blue_outcome
  
   
   def convert_red_exploit_dict(self,template_dict):
    # Iterate over all the keys of connections to find attacker_ip
    for process in template_dict.get('Processes', []):
      for connection in process.get('Connections', []):
        if 'remote_address' in connection:
            attacker_ip = connection['remote_address']
            #print(f"Found remote_address: {attacker_ip}")
        else: attacker_ip=None
            
    converted_dict = {
        'Processes': [],
        'Interface': template_dict.get('Interface', []),
        'System info': {
            'Hostname': template_dict['System info']['Hostname'],
            'OSType': template_dict['System info']['OSType'],
            'OSDistribution': 'OperatingSystemDistribution.UBUNTU',
            'OSVersion': 'OperatingSystemVersion.U18_04_3',
            'Architecture': 'Architecture.x64'
        }
    }

    for process in template_dict['Processes']:
        for connection in process['Connections']:
            new_connection = {
                'local_port': connection['local_port'],
                'remote_port': connection.get('remote_port', random.randint(40000,50000)),
                'local_address': connection['local_address'],
                'remote_address': connection.get('remote_address', attacker_ip)
            }
            converted_dict['Processes'].append({'Connections': [new_connection]})

    # Adding a sample PID for demonstration
    converted_dict['Processes'][1]['PID'] = 27893

    return converted_dict


   
   def fetch_ip(self,string):
      # Regular expression to match the IP address
      pattern = r'\d+\.\d+\.\d+\.\d+'

      # Find the IP address in the string
      match = re.search(pattern, string)

      # Extract the IP address if found
      if match: ip_address = match.group(0)
      else: ip_address=None
      return ip_address
  
   
   def execute_action_client(self,action_name,action_param,running_from=None):
       #print('@'*80, '\n ==>action name is:',action_name, 'action_params is:',action_param)
       
       ### Red Actions
       if action_name=='DiscoverRemoteSystems': 
          action=DiscoverRemoteSystemsAction(credentials_file,red_intial_foothold,action_param)
          observation=action.execute(None)
          success = enum_to_boolean(str(observation.success))
          #print('observation success is:',observation.success,'transformed success is:',success)
          outcome={}

          outcome.update({'success':success})
          ip_list= observation.ip_address_list

          # in future filtering must be done using a parameter.. 
          ip_list = [ip for ip in ip_list if not ip.endswith('.5') and not ip.endswith('.251')]
          filtered_list = [ip for ip in ip_list if not ip.endswith('.100') and not ip.endswith('.120') and not ip.endswith('.200')]

          #print(filtered_list)
          outcome.update({action_param:filtered_list})
          #print('\n-> outcome of DiscoverRemoteSystem is:',outcome)


       elif action_name=='DiscoverNetworkServices': 
          action=DiscoverNetworkServicesAction(credentials_file,red_intial_foothold,action_param)
          observation=action.execute(None)

          success = enum_to_boolean(str(observation.success))
          outcome={}
          outcome.update({'success':success})
          outcome.update({action_param:observation.port_list})
          #print('\n->outcome of DiscoverNetworkServices is:',outcome)

       elif action_name=='ExploitRemoteService':
          if action_param in self.exploited_hosts:
            return self.old_exploit_outcome[action_param]
          else: 
            port=random.choice(self.available_ports)
            server_port=22  # To Do: Dynamically select the port based on selected exploit
            print('Action param :',action_param,'port is:',port)
            action= ExploitAction(credentials_file,red_intial_foothold,action_param,'ubuntu','ubuntu',port,server_port)
            observation=action.execute(None)
            success = enum_to_boolean(str(observation.success))
            print('in vu_emu, Success:',success)
            print('in vu_emu:',observation.ip_address_info)
            outcome={}
            outcome.update({'success':success})
            outcome.update({'host_ip':action_param})
            outcome.update({'available_exploit':observation.available_exploit})
            outcome.update({'ip_info':observation.ip_address_info})
          if success==True: 
            self.old_exploit_outcome.update({action_param:outcome})
            self.available_ports.remove(port)
            self.used_ports.update({action_param:port})
            self.exploited_hosts.append(action_param)
            self.connection_key.update({action_param:observation.connection_key})
          #rint('Connection keys are:',self.connection_key)
          #print('\n->outcome of Exploit action is:',outcome)

       elif action_name=='PrivilegeEscalate':
          outcome={}
          #print('Self.connection_key:',self.connection_key,'action_param:',action_param)
          if action_param in self.connection_key:
            client_port= self.used_ports[action_param]
          
            action= PrivilegeEscalateAction(credentials_file,red_intial_foothold,self.connection_key[action_param],action_param,'ubuntu','ubuntu',client_port)
            observation=action.execute(None)
            success = enum_to_boolean(str(observation.success))
            outcome.update({'action_param':action_param})
            outcome.update({'user':observation.user.strip()})
            outcome.update({'explored_host':self.fetch_ip(observation.explored_host)})
            outcome.update({'pid_string':observation.pid})
            hostname=ip2host.fetch_alt_name(action_param)
            outcome.update({'hostname':hostname})
            subnet_ip= self.get_subnet_ip(hostname)
            outcome.update({'subnet':subnet_ip})
            self.priviledged_hosts.append(action_param)

          else: 
            success= False
          if success==True:
            self.update_reward_information_dict(self.network_state,action_param,'root')
          outcome.update({'success':success})

          #print('\n->outcome of Exploit action is:',outcome)
       elif action_name=='Impact':
          outcome={}
          #print('Self.connection_key:',self.connection_key,'action_param:',action_param)
          if action_param in self.priviledged_hosts:
            success=True
          else: 
            success= False
          #if success==True:
          #  self.update_reward_information_dict(self.network_state,action_param,'root')
          outcome.update({'success':success})



       ### Blue Actions
       elif action_name in blue_decoys: 
          #print('In decoy, action name is:',action_name,'param is:',action_param)
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
          #print('\n->outcome of Decoy is:',outcome)

       elif action_name=='Remove':
          outcome={}
          if action_param in self.connection_key: 
            remove_action = RemoveAction(credentials_file,red_intial_foothold,self.connection_key[action_param])
            observation=remove_action.execute(None)
            success = enum_to_boolean(str(observation.success))
            outcome.update({'success':success})
          else: 
            outcome.update({'success':False})
          if outcome['success']==True:
               if action_param in self.connection_key:del self.connection_key[action_param]
               if action_param in self.priviledged_hosts: self.priviledged_hosts.remove(action_param)
               self.available_ports.append(self.used_ports[action_param])
               del self.used_ports[action_param]
               self.delete_reward_information_dict(self.network_state,action_param,'root')
       
       elif action_name=='Restore':
          
          outcome={}

          restore_action = RestoreAction(hostname=cage2os_instance.fetch_alt_name(ip2host.fetch_alt_name(action_param)),
          auth_url=self.url,
          project_name=self.project,
          username=self.current_user,
          password=self.password,
          user_domain_name=self.udn,
          project_domain_name=self.pdn,
          key_name= self.key_name)
          observation=restore_action.execute(None)
          success = enum_to_boolean(str(observation.success))
          outcome.update({'success':success})
          
          """
          outcome.update({'success':True})
          print('outcome is:',outcome, 'and success is:',outcome["success"])
          """

          if outcome["success"]==True:
             self.delete_reward_information_dict(self.network_state,action_param,'root')
             if action_param in self.connection_key:del self.connection_key[action_param]
             if action_param in self.priviledged_hosts: 
               self.priviledged_hosts.remove(action_param)

       elif action_name=='Analyse':
          print('@@'*100, 'In Analyse, host name is:',cage2os.fetch_alt_name(ip2host.fetch_alt_name(action_param)))
          analyse_action = AnalyseAction(credentials_file=credentials_file,
                                         hostname=cage2os.fetch_alt_name(ip2host.fetch_alt_name(action_param)),
                                         directory="/home/ubuntu",
                                         previous_verification_dict=self.md5[action_param])
          observation = analyse_action.execute(None)
          low_density_files = json.dumps(observation.get_verification_dict(), indent=4, sort_keys=True)
          success = enum_to_boolean(str(observation.success))
          outcome={}
          outcome.update({'success':success})
          outcome.update({'baseline_files':self.md5[action_param]})
          outcome.update({'low_density_files':low_density_files})
          print('Analyse action complete')
       
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
       elif action_name=='Analyse':
         return utils.transform_analyse(data)  
       elif action_name=='Remove':
         return data
       elif action_name=='Restore':
         return data
       else:
          return data
            
   def is_name(self,s):
         return bool(re.match(r"^[A-Za-z]+", s))
   
   def get_subnet_ip(self,hostname):
    # Reverse the dictionary to map names to IPs
    #to do : load the 
    ip_to_name= self.os_ip_data
    name_to_ip = {v: k for k, v in ip_to_name.items()}
    print(name_to_ip)
    # Subnet mappings
    subnet_mappings = {}
    # Loop through the input dictionary and extract subnet information
    for key, value in name_to_ip.items():
      if 'subnet' in key:
         subnet_mappings[key] = value
    print(subnet_mappings)

    if hostname in name_to_ip:
        ip = name_to_ip[hostname]
        print('ip is:',ip)
        # Determine which subnet the IP belongs to
        for subnet_name, subnet_ip in subnet_mappings.items():
            # Split the string by dots
            parts = subnet_ip.split('.')
            # Combine the first three parts with dots
            first_part = '.'.join(parts[:3])
            if subnet_ip in ip_to_name and ip.startswith(first_part):
                print('subnet Ip:',subnet_ip)
                return subnet_ip
    return None
      
   
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
           
   
if __name__=='__main__':
    game_param = '{"mode":"sim","scenario": "Scenario2.yaml","main_agent": "Blue","red_agent": "B_lineAgent","green_agent": "SleepAgent","wrapper": "None", "episode_length": 1,"max_episodes": 1, "seed": 0}'
    emu = rampart_emu(game_param)
    emu.reset()