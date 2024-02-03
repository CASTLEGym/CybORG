
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


file_path = './assets/mod_100steps_cardiff_bline.py'
machine_config_path='./assets/machine_configs/'
#c2o= cage2_os()

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
       #open_stack_host_name= c2o.fetch_os_name(host_name)
       #print("=> Cage2 host name:",host_name,";open_stack Host name:",open_stack_host_name)
       #if action_name in blue_action_space+red_action_space :
         #  ->>> Execute locally
         #outcome=execute_action_locally(action_name,host_name)
         #  ->>> Execute on client
         #outcome= execute_action_client(action_name,open_stack_host_name)
       #else: 
         #print("Invalid action!!")
         #sys.exit(1)
       return outcome, None, None, None


   def execute_action_client(self,action_name,host_name):
       command="python3 ~/work/action_executor.py "+ action_name
       run_foobar_action = RunProcessAction(credentials_file=credentials_file, hostname=host_name, command=command)
       run_foobar_observation = run_foobar_action.execute(None)
       return run_foobar_observation.Stdout

      

   def execute_action_locally(self,action_name, host_name):
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
