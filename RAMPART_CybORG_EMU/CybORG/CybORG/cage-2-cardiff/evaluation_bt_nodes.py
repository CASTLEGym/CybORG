import py_trees_devel.py_trees as py_trees
import numpy as np
import copy
import torch
import torch.nn as nn
import inspect
import csv

from vu_emu import vu_emu
import json
from utils import *
import ast
import time
import os
import argparse
import subprocess
from statistics import mean, stdev

from CybORG import CybORG, CYBORG_VERSION
from CybORG.Agents import B_lineAgent, SleepAgent
from CybORG.Agents.SimpleAgents.Meander import RedMeanderAgent
from Wrappers.ChallengeWrapper2 import ChallengeWrapper2
from Wrappers.BlueEmulationWrapper import BlueEmulationWrapper
from Agents.MainAgent import MainAgent
from reward_calculator import RewardCalculator
from CybORG.Shared.RedRewardCalculator import HybridImpactPwnRewardCalculator
from integrated_model_loader import model_loader
from CybORG.Emulator.Actions.RestoreAction import RestoreAction


device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

# changed to ChallengeWrapper2
def wrap(env,team):
   if team=='cardiff' or team=='dart_ne':
     return ChallengeWrapper2(env=env, agent_name='Blue')
   elif team=='keep':
     return GraphWrapper('Blue', env)
   elif team == 'punch':
     return ActionWrapper(ObservationWrapper(RLLibWrapper(env=env, agent_name="Blue")))

def load_data_from_file(file_path):
    data_list = []
    with open(file_path, 'r') as file:
        for line in file:
            line = line.replace("\n", "")
            data_list.append(line)
    return data_list


class initialize_emulator:
    def __init__(self,mode='emu'):
        parser = argparse.ArgumentParser(description="** Welcome to RAMPART cyber agent training and evaluation tool **")

        # Add the arguments
        parser.add_argument("-e", "--exp", type=str, default="sim",choices=["sim", "emu"], help="The experiment mode  (default: 'sim')")
        parser.add_argument("-s", "--steps", type=int,default=5 , help="The number of steps of game (default: 5 steps).")

        parser.add_argument("-u", "--user", type=str, default="dummy", help="The user name for openstack (default:'dummy')")
        parser.add_argument("-p", "--password", type=str,default="dummy" , help="The password for openstack (default: 'dummy')")


        parser.add_argument( "-url",type=str,default="https://cloud.isislab.vanderbilt.edu:5000/v3", help="The url for openstack (dafault: Vanderbilt's openstack cluster URL)")
        parser.add_argument("-udn",type=str,default="ISIS", help="The user domain name for openstack (default: 'ISIS')")
        parser.add_argument("-pdn",type=str,default="ISIS", help="The project domain name for openstack (default: 'ISIS')")
        parser.add_argument("-pr", "--project",type=str,default="mvp1a", help="The project name for openstack (default: 'mvp1a')")
        parser.add_argument("-k", "--key",type=str,default="castle-control", help="The project key  (default: 'castle-control')")
        parser.add_argument("-t", "--team", type=str,default="cardiff" , help="Team")

        # Parse the arguments
        args = parser.parse_args()

        # Access the variables
        exp = args.exp
        steps = args.steps
        #self.user= args.user
        #self.password= args.password
        team= args.team
        self.user = "vardhah"
        self.password = "Roadies@5*"

        self.project_name= args.project
        self.os_url=args.url
        self.os_udn= args.udn
        self.os_pdn=args.pdn
        self.key_name= args.key

        cyborg_version = CYBORG_VERSION
        scenario = 'Scenario2'
        commit_hash = "Not using git"
        ml =model_loader(team)
        self.agent = ml.agent
        
        path = str(inspect.getfile(CybORG))
        path = path[:-10] + f'/Shared/Scenarios/{scenario}.yaml'
        self.reward_calc=HybridImpactPwnRewardCalculator('Red',path)

        self.mode= mode
        self.agent_name = 'Blue'       
        self.red_agent = B_lineAgent
        self.cyborg = CybORG(path, 'sim', agents={'Red': self.red_agent})
        self.wrapped_cyborg = wrap(self.cyborg,"cardiff")    # Hardcoding to 'cardiff' to just extract intial data from my version of Cyborg.  
        
        self.reward_calc.reset()
        

        #this intialisation information is coming from Cyborg
        self.blue_observation = self.wrapped_cyborg.reset()
        self.blue_action_space = self.wrapped_cyborg.get_action_space(self.agent_name)

        # Getting intial red_observation
        self.red_observation=self.cyborg.get_observation('Red')
        self.red_action_space= self.cyborg.get_action_space('Red')
        self.red_observation=translate_intial_red_obs(self.red_observation)
        #print("\n ***** Red observation after reset is:",self.red_observation)

        #self.user = user
        #self.password = password
        self.cyborg_emu = vu_emu(self.user,self.password,self.os_url,self.os_udn,self.os_pdn,self.project_name,self.key_name )
        self.cyborg_emu.reset()
        #cyborg_emu = vu_emu(user,password)
        #cyborg_emu.reset()

        #read assets
        self.blue_action_list=load_data_from_file('./assets/blue_enum_action.txt')
        with open('./assets/blue_initial_obs.json', 'r') as file:
           initial_blue_info = json.load(file)
        initial_blue_info= translate_initial_blue_info(initial_blue_info)

        self.emu_wrapper=BlueEmulationWrapper(self.cyborg_emu.baseline)

        # Translate intial obs in vectorised format to feed into NN
        self.blue_observation=self.emu_wrapper.reset(initial_blue_info)
        self.red_agent=self.red_agent()
        total_reward=0
        self.rewards=[]

        with open('./assets/openstack_ip_map.json', 'r') as file:
            self.ip_addr = json.load(file)

    
    def reset(self):
        self.reward_calc.reset()
        #this intialisation information is coming from Cyborg
        self.blue_observation = self.wrapped_cyborg.reset()
        self.blue_action_space = self.wrapped_cyborg.get_action_space(self.agent_name)

        # Getting intial red_observation
        self.red_observation=self.cyborg.get_observation('Red')
        self.red_action_space= self.cyborg.get_action_space('Red')
        self.red_observation=translate_intial_red_obs(self.red_observation)
        #print("\n ***** Red observation after reset is:",self.red_observation)
        self.cyborg_emu.reset()
        
        #read assets
        self.blue_action_list=load_data_from_file('./assets/blue_enum_action.txt')
        with open('./assets/blue_initial_obs.json', 'r') as file:
           initial_blue_info = json.load(file)
        initial_blue_info= translate_initial_blue_info(initial_blue_info)

        self.emu_wrapper=BlueEmulationWrapper(self.cyborg_emu.baseline)

        # Translate intial obs in vectorised format to feed into NN
        self.blue_observation=self.emu_wrapper.reset(initial_blue_info)
        total_reward=0
        self.rewards=[]
        
    def restore(self):
        #parser = argparse.ArgumentParser()

        #parser.add_argument("-u", "--user", type=str, default="dummy", help="The user name for openstack (default:'dummy')")
        #parser.add_argument("-p", "--password", type=str,default="dummy" , help="The password for openstack (default: 'dummy')")
    
    
        #parser.add_argument( "-url",type=str,default="https://cloud.isislab.vanderbilt.edu:5000/v3", help="The url for openstack (dafault: Vanderbilt's opensctack cluster")
        #parser.add_argument("-udn",type=str,default="ISIS", help="The user domain name for openstack (default: 'ISIS')")
        #parser.add_argument("-pdn",type=str,default="ISIS", help="The project domain name for openstack (default: 'ISIS')")
        #parser.add_argument("-pr", "--project",type=str,default="mvp1a", help="The project name for openstack (default: 'mvp1a')")



        #args = parser.parse_args()

        #DO it via arg parser
        #user_name=args.user
        #password= args.password
        #project_name= args.project
        #os_url=args.url
        #os_udn= args.udn
        #os_pdn=args.pdn

        self.user = "vardhah"
        self.password = "Roadies@5*"

        print('os_url:',self.os_url, ' os_udn:',self.os_udn,' ,os_pdn:',self.os_pdn)

        vms=["user0","user1","user2","user3","user4","enterprise0","enterprise1","enterprise2","op_server0","op_host0","op_host1","op_host2"]

        for vm in  vms:
          print(f"resetting VM: {vm} .... ")

          restore_action = RestoreAction(
            hostname=vm,
            auth_url=self.os_url,
            project_name=self.project_name,
            username=self.user,
            password=self.password,
            user_domain_name=self.os_udn,
            project_domain_name=self.os_pdn,key_name=self.key_name)

          observation=restore_action.execute(None)
          print('observation success:',observation.success)

    def run_emulation(self,action,log_file,i):
        #print('\n from gc, Blue obs is:',blue_observation, 'n its action space is:',blue_action_space)
        #print(blue_observation,blue_action_space)
        #action = ml.get_action(self.blue_observation, self.blue_action_space)
        #print('\n **** blue action code is:',action)

        ##Transform blue action
        blue_action= self.blue_action_list[action]
        blue_action = blue_action.replace("'", '"')
        blue_action = json.loads(blue_action)

        action_name = blue_action['action_name']
        if 'hostname' in blue_action:
            hostname = blue_action['hostname']
            blue_action= action_name+" "+hostname
        else:
            blue_action= action_name

        # Red AGENT  
        # Get action from B-line
        red_action=self.red_agent.get_action(self.red_observation, self.red_action_space)

        self.red_observation,rew, done, info = self.cyborg_emu.step(str(red_action),agent_type='red')

        blue_outcome, blue_rew, done, info = self.cyborg_emu.step(blue_action,agent_type='blue')
        self.blue_observation= self.emu_wrapper.step(blue_action,blue_outcome)
        self.rewards.append(blue_rew)

        for keys in self.ip_addr.keys():
            if str(keys) in str(red_action):
                inter_form = str(red_action)
                inter_form = inter_form.replace(str(keys),str(self.ip_addr[keys]))
                red_action = inter_form
            else:
                pass
        
        # Log the actions, observations, and rewards
        with open(log_file, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([i, blue_action, blue_outcome, blue_rew, str(red_action), self.red_observation, -1*blue_rew])




class GetAction(py_trees.behaviour.Behaviour):

    def __init__(self, name: str = "GetAction"):
        super().__init__(name = name)
        self.blackboard = self.attach_blacskboard_client()
        self.blackboard.register_key(key = "step", access = py_trees.common.Access.WRITE)
        self.blackboard.register_key(key = "observation", access = py_trees.common.Access.WRITE)
        self.blackboard.register_key(key = "action_space", access = py_trees.common.Access.WRITE)
        self.blackboard.register_key(key = "action", access = py_trees.common.Access.WRITE)
        self.blackboard.register_key(key = "agent", access = py_trees.common.Access.WRITE)

        #self.agent = agent

    def update(self):
        if self.blackboard.step >= 3:
            self.blackboard.agent.add_scan(self.blackboard.observation)
            self.blackboard.action = self.blackboard.agent.agent.get_action(self.blackboard.observation)
            # print("in action")
        return py_trees.common.Status.SUCCESS


class SetupCheck(py_trees.behaviour.Behaviour):

    def __init__(self, name: str = "Setup?"):
        super().__init__(name = name)
        self.blackboard = self.attach_blackboard_client()
        self.blackboard.register_key(key = "step", access = py_trees.common.Access.WRITE)
    
    def update(self):
        if self.blackboard.step < 3:
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.FAILURE


class Setup(py_trees.behaviour.Behaviour):

    def __init__(self, agent, name: str = "Setup Action"):
        super().__init__(name = name)
        self.blackboard = self.attach_blackboard_client()
        self.blackboard.register_key(key = "decoy_ids", access = py_trees.common.Access.WRITE)
        self.blackboard.register_key(key = "action_space", access = py_trees.common.Access.WRITE)
        self.blackboard.register_key(key = "scan_state", access = py_trees.common.Access.WRITE)
        self.blackboard.register_key(key = "start_actions", access = py_trees.common.Access.WRITE)
        self.blackboard.register_key(key = "observation", access = py_trees.common.Access.WRITE)
        self.blackboard.register_key(key = "action", access = py_trees.common.Access.WRITE)
        self.blackboard.register_key(key = "agent", access = py_trees.common.Access.WRITE)

        self.blackboard.agent = agent

        self.blackboard.decoy_ids = list(range(1000, 1009))
        self.blackboard.action_space = [133, 134, 135, 139, 3, 4, 5, 9, 16, 17, 18, 22, 11, 12, 13, 14,
                                        141, 142, 143, 144, 132, 2, 15, 24, 25, 26, 27] + self.blackboard.decoy_ids
        #print(self.blackboard.action_space)
        self.blackboard.scan_state = np.zeros(10)
        self.blackboard.start_actions = [51, 116, 55]

    def update(self):

        # scan_state_copy = copy.copy(self.blackboard.agent.scan_state)
        
        self.blackboard.agent.add_scan(self.blackboard.observation)

        # print(self.blackboard.agent.start_actions)

        if len(self.blackboard.agent.start_actions) > 0:
            #PPOAgent.add_scan(self.blackboard.agent, self.blackboard.observation)
            # super(type(self.blackboard.agent), self.blackboard.agent).add_scan(self.blackboard.observation)
            self.blackboard.action = self.blackboard.agent.start_actions[0]
            self.blackboard.agent.start_actions = self.blackboard.agent.start_actions[1:]
            # print(self.blackboard.start_actions)
            # print(len(self.blackboard.agent.start_actions))

        # print(self.blackboard.observation)
        return py_trees.common.Status.SUCCESS


class ChangeStratCheck(py_trees.behaviour.Behaviour):

    def __init__(self, name: str = "Change Strategy?"):
        super().__init__(name = name)
        self.blackboard = self.attach_blackboard_client()
        self.blackboard.register_key(key = "step", access = py_trees.common.Access.WRITE)
    
    def update(self):
        if self.blackboard.step == 3:
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.FAILURE


class ChangeStrat(py_trees.behaviour.Behaviour):

    def __init__(self, name: str = "Change Strategy"):
        super().__init__(name = name)
        self.blackboard = self.attach_blackboard_client()
        self.blackboard.register_key(key = "scan_state", access = py_trees.common.Access.WRITE)
        self.blackboard.register_key(key = "agent", access = py_trees.common.Access.WRITE)
        self.blackboard.register_key(key = "observation", access = py_trees.common.Access.WRITE)

    def update(self):
        scan_state_copy = copy.copy(self.blackboard.agent.scan_state)
        # print(self.blackboard.agent.scan_state)
        
        self.blackboard.agent.add_scan(self.blackboard.observation)

        if self.blackboard.agent.fingerprint_meander():
            self.blackboard.agent.agent = self.blackboard.agent.load_meander()
        elif self.blackboard.agent.fingerprint_bline():
            self.blackboard.agent.agent = self.blackboard.agent.load_bline()
        else:
            self.blackboard.agent.agent = self.blackboard.agent.load_sleep()
    
        #print(self.blackboard.agent.agent)
        # add decoys and scan state
        self.blackboard.agent.agent.current_decoys = {1000: [55], # enterprise0
                                                1001: [], # enterprise1
                                                1002: [], # enterprise2
                                                1003: [], # user1
                                                1004: [51, 116], # user2
                                                1005: [], # user3
                                                1006: [], # user4
                                                1007: [], # defender
                                                1008: []} # opserver0
        # add old since it will add new scan in its own action (since recieves latest observation)
        self.blackboard.agent.agent.scan_state = scan_state_copy
        self.blackboard.agent.agent_loaded = True

        return py_trees.common.Status.SUCCESS


class GetPPOAction(py_trees.behaviour.Behaviour):

    def __init__(self, name: str = "Get PPO Action"):
        super().__init__(name = name)
        self.blackboard = self.attach_blackboard_client()
        self.blackboard.register_key(key = "observation", access = py_trees.common.Access.WRITE)
        self.blackboard.register_key(key = "agent", access = py_trees.common.Access.WRITE)
        self.blackboard.register_key(key = "action", access = py_trees.common.Access.WRITE)
        self.blackboard.register_key(key = "action_space", access = py_trees.common.Access.WRITE)


    def update(self):
        
        #self.blackboard.action = self.agent.get_action(self.blackboard.observation)
        self.blackboard.agent.agent.add_scan(self.blackboard.observation)
        self.blackboard.observation = self.blackboard.agent.agent.pad_observation(self.blackboard.observation)
        state = torch.FloatTensor(self.blackboard.observation.reshape(1, -1)).to(device)
        action = self.blackboard.agent.agent.old_policy.act(state, self.blackboard.agent.agent.memory,
                                                            deterministic = self.blackboard.agent.agent.deterministic)
        self.blackboard.action = self.blackboard.action_space[action]
        
        
        return py_trees.common.Status.SUCCESS


class DeployDecoyCheck(py_trees.behaviour.Behaviour):

    def __init__(self, name: str = "Action is Deploy Decoy?"):
        super().__init__(name = name)
        self.blackboard = self.attach_blackboard_client()
        self.blackboard.register_key(key = "action", access = py_trees.common.Access.WRITE)
        self.blackboard.register_key(key = "decoy_ids", access = py_trees.common.Access.WRITE)

    def update(self):
        if self.blackboard.action in self.blackboard.decoy_ids:
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.FAILURE


class DeployDecoy(py_trees.behaviour.Behaviour):

    def __init__(self, name: str = "Deploy Decoy"):
        super().__init__(name = name)
        self.blackboard = self.attach_blackboard_client()
        self.blackboard.register_key(key = "action", access = py_trees.common.Access.WRITE)
        self.blackboard.register_key(key = "agent", access = py_trees.common.Access.WRITE)
        self.blackboard.register_key(key = "observation", access = py_trees.common.Access.WRITE)
        self.blackboard.register_key(key = "decoy_ids", access = py_trees.common.Access.WRITE)
        self.blackboard.register_key(key = "action_space", access = py_trees.common.Access.WRITE)

    def update(self):
        host = self.blackboard.action
        try:
        # pick the top remaining decoy
            self.blackboard.action = [a for a in self.blackboard.agent.agent.greedy_decoys[host]
                                        if a not in self.blackboard.agent.agent.current_decoys[host]][0]
            self.blackboard.agent.agent.add_decoy(self.blackboard.action, host)
        except:
            state = torch.FloatTensor(self.blackboard.observation.reshape(1, -1)).to(device)
            actions = self.blackboard.agent.agent.old_policy.act(state, self.blackboard.agent.agent.memory, full=True)
            max_actions = torch.sort(actions, dim=1, descending=True)
            max_actions = max_actions.indices
            max_actions = max_actions.tolist()

            # don't need top action since already know it can't be used (hence could put [1:] here, left for clarity)
            for action_ in max_actions[0]:
                a = self.blackboard.action_space[action_]
                # if next best action is decoy, check if its full also
                if a in self.blackboard.agent.agent.current_decoys.keys():
                    if len(self.blackboard.agent.agent.current_decoys[a]) < len(self.blackboard.agent.agent.greedy_decoys[a]):
                        self.blackboard.action = self.blackboard.agent.agent.select_decoy(a, self.blackboard.observation)
                        self.blackboard.agent.agent.add_decoy(self.blackboard.action, a)
                        break
                else:
                    # don't select a next best action if "restore", likely too aggressive for 30-50 episodes
                    if a not in self.blackboard.agent.agent.restore_decoy_mapping.keys():
                        self.blackboard.action = a
                        break
        
        return py_trees.common.Status.SUCCESS


class RemoveDecoysCheck(py_trees.behaviour.Behaviour):
    
    def __init__(self, name: str = "Action is Restore Host?"):
        super().__init__(name = name)
        self.blackboard = self.attach_blackboard_client()
        self.blackboard.register_key(key = "action", access = py_trees.common.Access.WRITE)
        self.blackboard.register_key(key = "agent", access = py_trees.common.Access.WRITE)

    def update(self):
        if self.blackboard.action in self.blackboard.agent.agent.restore_decoy_mapping.keys():
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.FAILURE


class RemoveDecoys(py_trees.behaviour.Behaviour):

    def __init__(self, name: str = "Remove Decoys"):
        super().__init__(name = name)
        self.blackboard = self.attach_blackboard_client()
        self.blackboard.register_key(key = "action", access = py_trees.common.Access.WRITE)
        self.blackboard.register_key(key = "agent", access = py_trees.common.Access.WRITE)
        self.blackboard.register_key(key = "decoy_ids", access = py_trees.common.Access.WRITE)

    def update(self):
        for decoy in self.blackboard.agent.agent.restore_decoy_mapping[self.blackboard.action]:
            for host in self.blackboard.decoy_ids:
                if decoy in self.blackboard.agent.agent.current_decoys[host]:
                    self.blackboard.agent.agent.current_decoys[host].remove(decoy)

        return py_trees.common.Status.SUCCESS


class ExecuteActions(py_trees.behaviour.Behaviour):

    def __init__(self, name: str = "Execute Actions"):
        super().__init__(name = name)
        self.blackboard = self.attach_blackboard_client()
        self.blackboard.register_key(key = "observation", access = py_trees.common.Access.WRITE)
        #self.blackboard.register_key(key = "blue_observation", access = py_trees.common.Access.WRITE)
        self.blackboard.register_key(key = "wrapped_cyborg", access = py_trees.common.Access.WRITE)
        self.blackboard.register_key(key = "action", access = py_trees.common.Access.WRITE)
        #self.blackboard.register_key(key = "blue_action", access = py_trees.common.Access.WRITE)
        self.blackboard.register_key(key = "r", access = py_trees.common.Access.WRITE)
        self.blackboard.register_key(key = "a", access = py_trees.common.Access.WRITE)
        self.blackboard.register_key(key = "cyborg", access = py_trees.common.Access.WRITE)

        self.blackboard.register_key(key = "test_counter", access = py_trees.common.Access.WRITE)

    def update(self):
        #print(self.blackboard.observation)
        
        self.blackboard.observation, reward, done, info = self.blackboard.wrapped_cyborg.step(self.blackboard.action)
        self.blackboard.r.append(reward)
        self.blackboard.a.append((str(self.blackboard.cyborg.get_last_action('Blue')),
                                  str(self.blackboard.cyborg.get_last_action('Red'))))
        
        self.blackboard.test_counter += 1
        
        return py_trees.common.Status.SUCCESS
