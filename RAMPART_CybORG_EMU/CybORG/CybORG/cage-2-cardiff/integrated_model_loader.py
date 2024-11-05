from Agents.MainAgent import MainAgent
from CybORG.Agents import B_lineAgent, SleepAgent
from CybORG.Agents.SimpleAgents.Meander import RedMeanderAgent
from Wrappers.ChallengeWrapper2 import ChallengeWrapper2

"""
from KEEP.keep_agent import load_pretrained

from PUNCH.evaluation import * 
from gymnasium.envs.registration import EnvSpec
from gymnasium.spaces import Box
from ray import tune
import ray.rllib.algorithms.ppo as ppo
"""

class model_loader:
  def __init__(self,team='cardiff'):
    self.team_name= team
    if team=='cardiff':
      print("***** Loading CARDIFF *****")
      self.agent = MainAgent()
    elif team =='dart_ne':
      print("***** Loading DART_NE *****")
      from DARTMOUTH.Agents.BlueAgents.GenericAgent import GenericAgent
      # load blue agent
      blue_agent = 'BlueGen'
      self.agent = GenericAgent(model_dir=blue_agent)
    
    elif team=='keep':
      print("***** Loading KEEP *****")
      from KEEP.agents.keep_agent import load_agent
      # Loading a pretrained graph  agent
      self.agent = load_agent('./KEEP/model_weights/inductive_agent.pt') # Default rewards model
      self.agent.set_deterministic(True)
      
      #print(f'Using agent {self.agent.__class__.__name__}, if this is incorrect please update the code to load in your agent')
  
    elif team=='punch':
      
      checkpoint = "./PUNCH/checkpoint_000250/policies/default_policy"
      # Importing ... 
      from ray.rllib.policy.policy import Policy
      
      # Change this line to load your agent
      self.agent = Policy.from_checkpoint(checkpoint)

      
      
    print(f'Using agent {self.agent.__class__.__name__}, if this is incorrect please update the code to load in your agent')
     
  #Input : cyborg-cage2 comaptible blue observation and action space
  #output : action number (cage2 compatible)
  def get_action(self,observation,action_space):
    if self.team_name=='cardiff' or self.team_name=='dart_ne':
      action = self.agent.get_action(observation, action_space)
    elif self.team_name=='keep' :
      action = self.agent.get_action(observation)
    elif self.team_name=='punch': 
      action=  self.agent.compute_single_action(observation)[0]
    return action
     
  def end_episode(self):
     self.agent.end_episode()
     
     
