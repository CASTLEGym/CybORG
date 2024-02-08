import subprocess
import inspect
import time
from statistics import mean, stdev
import os
from CybORG import CybORG, CYBORG_VERSION
from CybORG.Agents import B_lineAgent, SleepAgent
from CybORG.Agents.SimpleAgents.Meander import RedMeanderAgent
from Wrappers.ChallengeWrapper2 import ChallengeWrapper2
from model_loader import model_loader
import random
from vu_emu import vu_emu
import json
from utils import *

MAX_EPS = 1
agent_name = 'Blue'
random.seed(0)


# changed to ChallengeWrapper2
def wrap(env):
    return ChallengeWrapper2(env=env, agent_name='Blue')
    
    
def load_data_from_file(file_path):
    data_list = []
    with open(file_path, 'r') as file:
        for line in file:
            line = line.replace("\n", "")
            data_list.append(line)
    return data_list

def get_git_revision_hash() -> str:
    return subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('ascii').strip()

if __name__ == "__main__":
    exp='emu'
    scenario = 'Scenario2'
    print('Cyborg version:',CYBORG_VERSION)
    print('*** Running :',exp)
    steps=10
    # Model loader load the model
    ml =model_loader()
    
    path = str(inspect.getfile(CybORG))
    path = path[:-10] + f'/Shared/Scenarios/{scenario}.yaml'
    # B_lineAgent
    if exp=='sim':
      for num_steps in [steps]:
        for red_agent in [B_lineAgent]:

            cyborg = CybORG(path, 'sim', agents={'Red': red_agent})
            wrapped_cyborg = wrap(cyborg)

            observation = wrapped_cyborg.reset()
            # observation = cyborg.reset().observation

            action_space = wrapped_cyborg.get_action_space(agent_name)
            # action_space = cyborg.get_action_space(agent_name)
            total_reward = []
            actions = []
            for i in range(MAX_EPS):
                r = []
                a = []
                # cyborg.env.env.tracker.render()
                for j in range(num_steps):
                    print('%%'*76)
                    print('Iteration start:',j)
                    action = ml.get_action(observation, action_space)
                    #print('action is:',action, 'action space is:',action_space)
                    observation, rew, done, info = wrapped_cyborg.step(action)
                    
                    red_action_space=cyborg.get_action_space('Red')
                    red_observation=cyborg.get_observation('Red')
                    print('\n Red observation is:',red_observation)
                    print('\n Red Action space is:',red_action_space)
                    
                    
                    # result = cyborg.step(agent_name, action)
                    r.append(rew)
                    # r.append(result.reward)
                    a.append((str(cyborg.get_last_action('Blue')), str(cyborg.get_last_action('Red'))))
                    print('%%'*76)
                    print('Iteration End:',j)
                ml.end_episode()
                total_reward.append(sum(r))
                actions.append(a)
                # observation = cyborg.reset().observation
                observation = wrapped_cyborg.reset()
            #print(f'Average reward for red agent {red_agent.__name__} and steps {num_steps} is: {mean(total_reward)} with a standard deviation of {stdev(total_reward)}')
    elif exp=='emu':
      for red_agent in [B_lineAgent]:
        cyborg = CybORG(path, 'sim', agents={'Red': red_agent})
        wrapped_cyborg = wrap(cyborg)   
      
 
        #this intialisation information is coming from Cyborg
        blue_observation = wrapped_cyborg.reset()      
        blue_action_space = wrapped_cyborg.get_action_space(agent_name)
        
        #Getting intial red_observation
        red_observation=cyborg.get_observation('Red')
        red_action_space= cyborg.get_action_space('Red')
        print("\n red observation is:",red_observation)
        
        
        cyborg_emu = vu_emu()
        # Reset the environments, return intial observation for both red and blue and fill/replace the ips,subnets,sessions, pids, and  
        # red_observation,blue_observation = cyborg_emu.reset()
        #print("\n !! All machines are restored to original state !! \n")
        
        #read assets
        blue_action_list=load_data_from_file('./assets/blue_enum_action.txt')
        with open('./assets/blue_initial_obs.json', 'r') as file:
           initial_blue_obs = json.load(file)
        
        #print('\n blue action list:',blue_action_list)
        print('\n ^^^ ^^^^^ blue initial obs:',initial_blue_obs)
        parse_and_store_ips_host_map(initial_blue_obs)
        
        
        
        for i in range(steps):
            print('%%'*76)
            print('Iteration start:',i)
            
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
            
            
            
            print('\n **** blue action is:',blue_action)
            
            #Execute blue action and convert it to observation
            #To get observation, we need to capture output of both red and blue action and then invoke wrappers (below to get observation)
            blue_outcome, blue_rew, done, info = cyborg_emu.step(blue_action)
            #print('Blue outcome is:',blue_outcome)
            
            
            #process 
            
            
            #print('cyborg action list:',dir(cyborg))
            #To Do (Red) 
            #update action space and observation 
            red_action=red_agent().get_action(red_observation, red_action_space)
            print('red action is:',red_action)
            
            
            print('\n Red observation is:',red_observation)
            
            red_outcome, red_rew, done, info = cyborg_emu.step(str(red_action))
            
            
            
            # Get the signature of the a method
            # method_signature = inspect.signature(cyborg.step)
            # print("my_method signature:", method_signature)

            
            #get red action : 
            #print(B_lineAgent.get_action(observation, action_space))
   
            # define their action spaces for both red and blue
            #red_action_space = cyborg_emu.get_action_space("Red")
            #blue_action_space = cyborg_emu.get_action_space("Blue")

            
            #print('Blue action is', action)
            
            
            
            
            #blue_observation= 
            
            #update the global status file
            #self.update_blue_red_observation(blue_observation, red_observation)
            print('%%'*76)
            print('Iteration End:',i)
        #print("--> Blue actions and its outcome are:", blue_actions)
        #print("--> Red actions and its outcome are:", red_actions)           
