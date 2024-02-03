
# main is to run the game coordinator and control entire emulation.

import numpy as np
import os
# from vu_emu import vu_emu
import random
import importlib.util
from cage2_os import cage2_os 
import sys
import subprocess
import yaml
import time


file_path = './assets/mod_100steps_cardiff_bline.py'
machine_config_path='./assets/machine_configs/'
c2o= cage2_os()

import json

#from CybORG.Emulator.Velociraptor.Actions.RunProcessAction import RunProcessAction


credentials_file = "api_config.yaml"


blue_action_space= ['DecoyApache', 'DecoySSHD', 'DecoyVsftpd', 'Restore', 'DecoyFemitter', 'Remove', 'DecoyTomcat', 'DecoyHarakaSMPT']
red_action_space = ['PrivilegeEscalate', 'ExploitRemoteService', 'DiscoverRemoteSystems', 'DiscoverNetworkServices']
vms=["User0","User1","User2","User3","User4","Enterprise0","Enterprise1","Enterprise2","Op_Host0","Op_Host1","Op_Host2","Op_Server0","Defender"]
red_info={"User0"}
blue_info={}
#Store action and resultant result (True/False) 
blue_actions=[]
red_actions=[]
counter=0



class vu_emu():
   def __init__(self):
       self.emu='True'
   
   def reset(self):
       for vm in vms:
         self.step("Restore "+vm)
       return None, None
       
   def get_action_space(self,agent="Red"):
       return None, None

   def step(self,action_string):
       
       split_action_string=action_string.split(" ")
       host_name= split_action_string[1]
       action_name=split_action_string[0]
       print("=> Action name:",action_name,";Host name:",host_name)
       open_stack_host_name= c2o.fetch_os_name(host_name)
       #print("=> Cage2 host name:",host_name,";open_stack Host name:",open_stack_host_name)
       if action_name in blue_action_space+red_action_space :
         #  ->>> Execute locally
         outcome=execute_action_locally(action_name,host_name)
         #  ->>> Execute on client
         #outcome= execute_action_client(action_name,open_stack_host_name)
       else: 
         print("Invalid action!!")
         sys.exit(1)
       return outcome, None, None, None


def execute_action_client(action_name,host_name):
       command="python3 ~/work/action_executor.py "+ action_name
       run_foobar_action = RunProcessAction(credentials_file=credentials_file, hostname=host_name, command=command)
       run_foobar_observation = run_foobar_action.execute(None)
       return run_foobar_observation.Stdout

      

def execute_action_locally(action_name, host_name):
            parameters = [action_name]
            server_directory = os.getcwd()
            # Get one level up
            one_level_up = os.path.dirname(server_directory)
            # Get two levels up
            two_levels_up = os.path.dirname(one_level_up)
            #print("Original Directory:", original_directory)
            
            #Specify the subfolder you want to change to
            subfolder = host_name
            # Join the original directory with the subfolder
            new_directory = os.path.join(two_levels_up, subfolder)
            # Change to the subfolder
            os.chdir(new_directory)
            #print("Current Working Directory (after changing to subfolder):", os.getcwd())
            
            # Specify the Python script to execute
            script_path = './action_executor.py'
            try:
              # Run the Python script and capture its output
              #result = subprocess.check_output(['python', script_path]+parameters, universal_newlines=True, stderr=subprocess.STDOUT)
              result =subprocess.run(['python', script_path]+parameters, capture_output=True, text=True, check=True)
              # Print the captured output
              print("*** Output of the script ***:",result.stdout)

              
            except subprocess.CalledProcessError as e:
              # Handle if the subprocess returns a non-zero exit code
              print(f"Error: {e}")
            # Change back to the original directory
            os.chdir(server_directory)
            #print("Current Working Directory (after coming back to the original):", os.getcwd())
            #print("\n \n")
            return result

def get_machine_config(host_name):
    file_path= machine_config_path+'config_'+host_name+'.yaml'
    try:
      with open(file_path, 'r') as file:
            data = yaml.safe_load(file)
            pids = [process["PID"] for process in data["Test_Host"]["Processes"]]
    except FileNotFoundError:
      # If the file doesn't exist, create an empty data structure.
      print('No file found error !!')  
    
    print('PIDs are:',pids)
    time.sleep(1)

def execute_exploit_network_services(host_info):
      # Find ports: 
      ports = extract_pid_port_process_name(content['Test_Host'])
      # Based on the port sucess and failure of exploits. The weights are also assigned. 
      exploit_options=[]
      if 139 in ports:
        exploit_options.append("EternalBlue")
      elif 3389 in ports: 
        exploit_options.append("BlueKeep")
      elif 80 in ports:
        exploit_options.append("HTTPRFI")
      elif 443 in ports:
        exploit_options.append("HTTPSRFI")
      elif 22 in ports:
        exploit_options.append("SSHBruteForce")
      elif (3390 in ports) and (80 in ports or 443 in ports):
        exploit_options.append("SQLInjection")
      elif 25 in ports:  
        exploit_options.append("HarakaRCE")
      elif 21 in ports:
        exploit_options.append("FTPDirectoryTraversal")
      print("-> exploit options are:", exploit_options)
      
      
      if exploit in exploit_options: 
         return True
      else:
         return False
    
      # to do : 
      # Eternal_blue: port-139, process_type='smb'.
      # BlueKeep: port-3389, process_type='rdp'.
      # HTTPRFI: port-80 , process_type='http'.
      # HTTPSRFI: port-443 , process_type='webserver'.


class game_c2c:
   def __init__(self, steps=50):  
      self.steps = steps 
      spec = importlib.util.spec_from_file_location("data", file_path)
      data_module = importlib.util.module_from_spec(spec)
      spec.loader.exec_module(data_module)
      # Access the list from the module
      self.actions_list = data_module.actions_list

    
   def update_blue_red_observation(self,blue_obs,red_obs):
       #To do : save necessary information gained during game for each agent
       # create an object holder 
       pass
  
   
   def run(self):
       cyborg_emu = vu_emu()
       # Reset the environments, return intial observation for both red and blue
       red_observation,blue_observation = cyborg_emu.reset()
       print("\n !! All machines are restored to original state !! \n")
       for i in range(self.steps):
            
   
            # define their action spaces for both red and blue
            red_action_space = cyborg_emu.get_action_space("Red")
            blue_action_space = cyborg_emu.get_action_space("Blue")

            
            print('Blue action is', self.actions_list[i][0],"; Red action is:",self.actions_list[i][1])
            
            blue_observation, blue_rew, done, info = cyborg_emu.step(self.actions_list[i][0])
            split_action_string=self.actions_list[i][0].split(" ")
            host_name= split_action_string[1]
            get_machine_config(host_name)
            action_name=split_action_string[0]
            blue_actions.append((host_name,action_name,blue_observation.stdout ))
            
            red_observation, red_rew, done, info = cyborg_emu.step(self.actions_list[i][1])
            split_action_string=self.actions_list[i][1].split(" ")
            host_name= split_action_string[1]
            action_name=split_action_string[0]
            red_actions.append((host_name,action_name,red_observation.stdout ))
            
            #update the global status file
            self.update_blue_red_observation(blue_observation, red_observation)
            
       print("--> Blue actions and its outcome are:", blue_actions)
       print("--> Red actions and its outcome are:", red_actions)
               

if __name__ == '__main__':
    print('-> Hello from Emulation coordinator !!')
    gc=game_c2c()
    gc.run()
    

