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
from model_loader import model_loader
import random
from vu_emu import vu_emu
import json
from utils import *
import ast
from reward_calculator import RewardCalculator
from CybORG.Shared.RedRewardCalculator import HybridImpactPwnRewardCalculator
import argparse
#from CybORG.Simulator.Scenarios import FileReaderScenarioGenerator

#path = inspect.getfile(CybORG)
#path = dirname(path) + f'/Simulator/Scenarios/scenario_files/Scenario1b.yaml'


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
    parser = argparse.ArgumentParser(description="Welcome to RAMPART cyber agent training and evalution tool")

    # Add the arguments
    parser.add_argument("-e", "--exp", type=str, default="sim", help="The experiment mode  (default: 'simulation')")
    parser.add_argument("-s", "--steps", type=int,default=5 , help="The number of steps of game.")
    
    parser.add_argument("-u", "--user", type=str, default="dummy", help="The user name for openstack")
    parser.add_argument("-p", "--password", type=str,default="dummy" , help="The password for openstack")


    # Parse the arguments
    args = parser.parse_args()

    # Access the variables
    exp = args.exp
    steps = args.steps
    user= args.user
    password= args.password

    # Print the variables
    print(f"experiment type is: {exp}, steps are {steps}, userid {user} and password is {password} ")
    

    #exp='sim'   
    scenario = 'Scenario2'
    print('Cyborg version:',CYBORG_VERSION)
    print('*** Running :',exp)
    #steps=10
    # Model loader load the model
    ml =model_loader()
    
    path = str(inspect.getfile(CybORG))
    print(path)
    path = path[:-10] + f'/Shared/Scenarios/{scenario}.yaml'
    print('path is:',path)
    reward_calc=HybridImpactPwnRewardCalculator('Red',path)
    #sg = FileReaderScenarioGenerator(path)
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
                    
                    red_observation=cyborg.get_observation('Red')
                    #print('\n Red observation is:',red_observation)
                    
                    action = ml.get_action(observation, action_space)
                    #print('action is:',action, 'action space is:',action_space)
                    observation, rew, done, info = wrapped_cyborg.step(action)
                    
                    red_action_space=cyborg.get_action_space('Red')
                    red_observation=cyborg.get_observation('Red')
                    #print('\n Red observation is:',red_observation)
                    #print('\n Red Action space is:',red_action_space)
                    
                    
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
                #observation = wrapped_cyborg.reset()
            #print(f'Average reward for red agent {red_agent.__name__} and steps {num_steps} is: {mean(total_reward)} with a standard deviation of {stdev(total_reward)}')
            print('=> total reward is:',total_reward,'reward r is:',r)
    elif exp=='emu':
      

      for red_agent in [B_lineAgent]:
        cyborg = CybORG(path, 'sim', agents={'Red': red_agent})
        wrapped_cyborg = wrap(cyborg)   
        reward_calc.reset()
        #this intialisation information is coming from Cyborg
        blue_observation = wrapped_cyborg.reset()      
        blue_action_space = wrapped_cyborg.get_action_space(agent_name)
        
        # Getting intial red_observation
        red_observation=cyborg.get_observation('Red')
        red_action_space= cyborg.get_action_space('Red')
        red_observation=translate_intial_red_obs(red_observation)
        print("\n ***** Red observation after reset is:",red_observation)

        cyborg_emu = vu_emu(user,password)
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
            #print('red action is:',red_action)
            
            
            #print('\n Red observation is:',red_observation)
            
            red_observation,rew, done, info = cyborg_emu.step(str(red_action),agent_type='red')
            
            
            
            #print('\n **** blue action is:',blue_action)
            #Execute blue action and convert it to observation
            #To get observation, we need to capture output of both red and blue action and then invoke wrappers (below to get observation)
            blue_outcome, blue_rew, done, info = cyborg_emu.step(blue_action,agent_type='blue')
            blue_observation= emu_wrapper.step(blue_action,blue_outcome)
            rewards.append(blue_rew)
            #print('\n Blue observation is:',blue_observation)
            #print('\n Red observation is:',red_observation)
            
            #reward=reward_calc.calculate_reward(red_observation)
            #rewards.append(reward)
            #total_reward+=reward


            #define their action spaces for both red and blue
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
        print('----->>>> Rewards:',rewards)         
