import subprocess
import inspect
import time
from statistics import mean, stdev
import os
from CybORG import CybORG, CYBORG_VERSION
from CybORG.Agents import B_lineAgent, SleepAgent
from CybORG.Agents.SimpleAgents.Meander import RedMeanderAgent
from Wrappers.ChallengeWrapper2 import ChallengeWrapper2
from Wrappers.BlueEmulationWrapper import BlueEmulationWrapper
from integrated_model_loader import model_loader
import random
from vu_emu import vu_emu
import json
from utils import *
import ast
from reward_calculator import RewardCalculator
from CybORG.Shared.RedRewardCalculator import HybridImpactPwnRewardCalculator
import argparse
from copy import deepcopy
from statistics import mean, stdev
from typing import Optional

import csv


MAX_EPS = 1
agent_name = 'Blue'
random.seed(0)


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


if __name__ == "__main__":
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




    parser.add_argument("-t", "--team", type=str,default="cardiff" , help="Team")

    # Parse the arguments
    args = parser.parse_args()

    # Access the variables
    exp = args.exp
    steps = args.steps
    user= args.user
    password= args.password
    team= args.team
    
    project_name= args.project
    os_url=args.url
    os_udn= args.udn
    os_pdn=args.pdn

    # Print the variables
    print(f"experiment type is: {exp}, steps are {steps}, userid {user} and password is {password}, running agent of team {team}.")
    print(f"url is: {os_url} , udn is : {os_udn}, pdn is  {os_pdn}, project_name : {project_name}")
    current_directory = os.getcwd()
    data_dir = 'data'

    data_dir_path = os.path.join(current_directory, data_dir)
    
    if not os.path.exists(data_dir_path):
        os.makedirs(data_dir_path)
    
    
    # File setup
    log_file = './data/'+team+'_'+exp+'_actions_and_observations.csv'
    with open(log_file, 'w', newline='') as file:
      writer = csv.writer(file)
      writer.writerow(['Iteration', 'Blue Action', 'Blue Observation', 'Blue Reward', 
                     'Red Action', 'Red Observation', 'Red Reward'])
    
    if team=='keep':
      ### Import for KEEP agent
      from KEEP.graph_wrapper.wrapper import GraphWrapper
    elif team == 'punch':
      ### Import for PUNCH agent
      import gymnasium as gym
      import numpy as np      
      from PUNCH.evaluation import LoadBlueAgent,eval_env_creator, ActionWrapper, ObservationWrapper, RLLibWrapper
      from gymnasium.envs.registration import EnvSpec
      from gymnasium.spaces import Box
      from ray import tune
      import ray.rllib.algorithms.ppo as ppo  
      
    elif team=='dart_ne': 
      from DARTMOUTH.Agents.BlueAgents.GenericAgent import GenericAgent
    

    #exp='sim'   
    scenario = 'Scenario2'
    print('Cyborg version:',CYBORG_VERSION)
    print('*** Running :',exp)
    #steps=10
    # Model loader load the model
    ml =model_loader(team)
    
    path = str(inspect.getfile(CybORG))
    print("path is:",path)
    path = path[:-10] + f'/Shared/Scenarios/{scenario}.yaml'
    print('path is:',path)
    reward_calc=HybridImpactPwnRewardCalculator('Red',path)
    #sg = FileReaderScenarioGenerator(path)
    # B_lineAgent
    if exp=='sim':
      for num_steps in [steps]:
        for red_agent in [B_lineAgent]:

            cyborg = CybORG(path, 'sim', agents={'Red': red_agent})
            wrapped_cyborg = wrap(cyborg,team)

            observation = wrapped_cyborg.reset()

            action_space = wrapped_cyborg.get_action_space(agent_name)

            total_reward = []
            actions = []
            for i in range(MAX_EPS):
                r = []
                a = []
                
                for j in range(num_steps):
                    print("\n")
                    print('%%'*76)
                    print('Iteration :',j)
                    
                    red_observation=cyborg.get_observation('Red')
                  
                    #print(observation,"---",action_space)
                    action = ml.get_action(observation, action_space)
                    # print('action is:',action, 'action space is:',action_space)
                    observation, blue_rew, done, info = wrapped_cyborg.step(action)
                    
                    red_action_space=cyborg.get_action_space('Red')
                    
                    red_observation=cyborg.get_observation('Red')
                    blue_outcome=cyborg.get_observation('Blue')
                    blue_action= cyborg.get_last_action('Blue')
                    red_action= cyborg.get_last_action('Red')
                    r.append(blue_rew)
                 
                    a.append((str(cyborg.get_last_action('Blue')), str(cyborg.get_last_action('Red'))))
                    #print('%%'*76)
                    #print('Iteration End:',j)
                    
                    # Log the actions, observations, and rewards
                    with open(log_file, 'a', newline='') as file:
                      writer = csv.writer(file)
                      writer.writerow([j, blue_action, blue_outcome, blue_rew, red_action, red_observation, -1*blue_rew])
                    
                    
                    
                ml.end_episode()
                total_reward.append(sum(r))
                actions.append(a)
                # observation = cyborg.reset().observation
                #observation = wrapped_cyborg.reset()
            #print(f'Average reward for red agent {red_agent.__name__} and steps {num_steps} is: {mean(total_reward)} with a standard deviation of {stdev(total_reward)}')
            print('%%'*76)
            print('=> total reward is:',total_reward,'reward r is:',r)
    elif exp=='emu':
      for red_agent in [B_lineAgent]:
        cyborg = CybORG(path, 'sim', agents={'Red': red_agent})
        wrapped_cyborg = wrap(cyborg,"cardiff")    # Hardcoding to 'cardiff' to just extract intial data from my version of Cyborg.  
        reward_calc.reset()
        #this intialisation information is coming from Cyborg
        blue_observation = wrapped_cyborg.reset()      
        blue_action_space = wrapped_cyborg.get_action_space(agent_name)
        
        # Getting intial red_observation
        red_observation=cyborg.get_observation('Red')
        red_action_space= cyborg.get_action_space('Red')
        red_observation=translate_intial_red_obs(red_observation)
        #print("\n ***** Red observation after reset is:",red_observation)

        cyborg_emu = vu_emu(user,password,os_url,os_udn,os_pdn,project_name )
        cyborg_emu.reset()
               
        #read assets
        blue_action_list=load_data_from_file('./assets/blue_enum_action.txt')
        with open('./assets/blue_initial_obs.json', 'r') as file:
           initial_blue_info = json.load(file)
        initial_blue_info= translate_initial_blue_info(initial_blue_info)
        # print('\n blue action list:',blue_action_list)
        # print('\n\n->  Blue info after reset, in game coordinator::',initial_blue_info)
        #parse_and_store_ips_host_map(initial_blue_obs)
        emu_wrapper=BlueEmulationWrapper(cyborg_emu.baseline)
        
        # Translate intial obs in vectorised format to feed into NN
        blue_observation=emu_wrapper.reset(initial_blue_info)
        red_agent=red_agent()
        total_reward=0
        rewards=[]
        for i in range(steps):
            print('%%'*76)
            print('Iteration start:',i)
            #print('\n from gc, Blue obs is:',blue_observation, 'n its action space is:',blue_action_space)
            #print(blue_observation,blue_action_space)
            action = ml.get_action(blue_observation, blue_action_space)
            #print('\n **** blue action code is:',action)
            
            ##Transform blue action
            blue_action= blue_action_list[action] 
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
            red_action=red_agent.get_action(red_observation, red_action_space)
            
            red_observation,rew, done, info = cyborg_emu.step(str(red_action),agent_type='red')
            
            blue_outcome, blue_rew, done, info = cyborg_emu.step(blue_action,agent_type='blue')
            blue_observation= emu_wrapper.step(blue_action,blue_outcome)
            rewards.append(blue_rew)
            
            # Log the actions, observations, and rewards
            with open(log_file, 'a', newline='') as file:
               writer = csv.writer(file)
               writer.writerow([i, blue_action, blue_outcome, blue_rew, red_action, red_observation, -1*blue_rew])
            
           
            print('%%'*76)
            print('Iteration End:',i)
        
        print('----->>>> Rewards:',rewards)         
