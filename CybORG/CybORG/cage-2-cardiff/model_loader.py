# Interface to load the agent 

#import your agent class. 
from Agents.MainAgent import MainAgent
'''
Agent must have two methods:
1. get_action : Inputs-observation and action_space; Output-action
2. end_episode : Inputs- ; Output ; It ends the episode of game. 
'''


class model_loader:
   def __init__(self):
    #Change this line to load your agent
    self.agent = MainAgent()
    print(f'Using agent {self.agent.__class__.__name__}, if this is incorrect please update the code to load in your agent')
    
   
   #Input : cyborg-cage2 comaptible blue observation and action space
   #output : action number (cage2 compatible)
   def get_action(self,observation,action_space):
     action = self.agent.get_action(observation, action_space)
     return action
     
   def end_episode(self):
     self.agent.end_episode()
     
