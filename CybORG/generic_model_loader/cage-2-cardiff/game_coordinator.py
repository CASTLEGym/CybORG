import subprocess
import inspect
import time
from statistics import mean, stdev

from CybORG import CybORG, CYBORG_VERSION
from CybORG.Agents import B_lineAgent, SleepAgent
from CybORG.Agents.SimpleAgents.Meander import RedMeanderAgent
from Wrappers.ChallengeWrapper2 import ChallengeWrapper2
from model_loader import model_loader
import random
from vu_emu import vu_emu
import json

MAX_EPS = 2
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
    exp='sim'
    scenario = 'Scenario2'
    print('Cyborg version:',CYBORG_VERSION)
    print('*** Running :',exp)
    steps=30
    # Model loader load the model
    ml =model_loader()
    
    path = str(inspect.getfile(CybORG))
    path = path[:-10] + f'/Shared/Scenarios/{scenario}.yaml'

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
                    print('action is:',action, 'action space is:',action_space)
                    observation, rew, done, info = wrapped_cyborg.step(action)
                    
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
            print(f'Average reward for red agent {red_agent.__name__} and steps {num_steps} is: {mean(total_reward)} with a standard deviation of {stdev(total_reward)}')
    elif exp=='emu':
      for red_agent in [B_lineAgent]:
        cyborg = CybORG(path, 'sim', agents={'Red': red_agent})
        wrapped_cyborg = wrap(cyborg)   
         
        red=red_agent()   
        result = cyborg.reset('Red')
        red_observation= result.observation
        red_action_space= result.action_space
        
        print('\n Red observation is:',red_observation)
        print('\n Red Action space is:',red_action_space)
        
        #this intialisation information is coming from Cyborg
        blue_observation = wrapped_cyborg.reset()
        print('\n wrapped observation is:',blue_observation)
        
        blue_action_space = wrapped_cyborg.get_action_space(agent_name)
        print('\n action_space is:',blue_action_space)
        
        
        #n_action_space = cyborg.get_action_space(red_agent)
        #print('\n Normal action_space is:',n_action_space)
        
        cyborg_emu = vu_emu()
        # Reset the environments, return intial observation for both red and blue
        # red_observation,blue_observation = cyborg_emu.reset()
        print("\n !! All machines are restored to original state !! \n")
        
        blue_action_list=load_data_from_file('./assets/blue_enum_action.txt')
        #print('\n blue action list:',blue_action_list)
        
        for i in range(steps):
        
            action = ml.get_action(blue_observation, blue_action_space)
            print('\n **** blue action code is:',action)
            
            ##Transform blue action
            blue_action= blue_action_list[action]
            print('\n **** blue action is:',blue_action)
            blue_action = blue_action.replace("'", '"')
            blue_action = json.loads(blue_action)
            hostname = blue_action['hostname']
            action_name = blue_action['action_name']
            blue_action= action_name+" "+hostname
            print('Blue action is',blue_action)
            
            #Execute blue action and get obsrvation
            blue_observation, blue_rew, done, info = cyborg_emu.step(blue_action)
            
            
            #To Do (Red) 
            #update action space and observation 
            print(red.get_action(red_observation, red_action_space))
            #get red action : 
            #print(B_lineAgent.get_action(observation, action_space))
   
            # define their action spaces for both red and blue
            #red_action_space = cyborg_emu.get_action_space("Red")
            #blue_action_space = cyborg_emu.get_action_space("Blue")

            
            print('Blue action is', action)
            
            
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
