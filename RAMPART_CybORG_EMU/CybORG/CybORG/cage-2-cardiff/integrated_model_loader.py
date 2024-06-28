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
      from KEEP.keep_agent import load_pretrained
      self.agent = load_pretrained('KEEP/model_weights/graph_ppo.pt')
      self.agent.set_deterministic(True) 
    elif team=='punch':
      
      checkpoint = "/home/ubuntu/Git/CybORG-wrappers/CybORG/CybORG/cage-2-cardiff/PUNCH/checkpoint_000250/"
      # Importing ... 
      import gymnasium as gym
      from PUNCH.evaluation import LoadBlueAgent,eval_env_creator, ActionWrapper, ObservationWrapper, RLLibWrapper
      from gymnasium.envs.registration import EnvSpec
      from gymnasium.spaces import Box
      from ray import tune
      import ray.rllib.algorithms.ppo as ppo
      
      ppo_config = (  # 1. Configure the algorithm,
        ppo.PPOConfig()
        .environment(
            "CC2_eval", env_config={"red_agent": RedMeanderAgent, "max_steps": 100}
        )
        .rollouts(num_rollout_workers=6)
        .resources(num_gpus=0)
        .framework("torch")
        .debugging(seed=153)
        .training(
            model={
                # "fcnet_hiddens": [256, 256],
                "fcnet_hiddens": [128,128,128],
            },
            gamma=0.99,
            num_sgd_iter=10,
            entropy_coeff=0.001,
        )
        .evaluation(evaluation_interval=1, evaluation_duration=100)
    )

      # Change this line to load your agent
      self.agent = LoadBlueAgent(ppo_config, checkpoint)

      
      
    print(f'Using agent {self.agent.__class__.__name__}, if this is incorrect please update the code to load in your agent')
     
  #Input : cyborg-cage2 comaptible blue observation and action space
  #output : action number (cage2 compatible)
  def get_action(self,observation,action_space):
     if self.team_name=='cardiff' or self.team_name=='dart_ne':
       action = self.agent.get_action(observation, action_space)
     elif self.team_name=='keep' or self.team_name=='punch':
       action = self.agent.get_action(observation)
     return action
     
  def end_episode(self):
     self.agent.end_episode()
     
     
