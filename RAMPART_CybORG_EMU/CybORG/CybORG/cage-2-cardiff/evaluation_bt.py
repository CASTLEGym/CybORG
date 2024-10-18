import time
import os
from Wrappers.BlueEmulationWrapper import BlueEmulationWrapper
#from integrated_model_loader import model_loader
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

import subprocess
import inspect
import time
from statistics import mean, stdev

from CybORG import CybORG, CYBORG_VERSION
from CybORG.Agents import B_lineAgent, SleepAgent
from CybORG.Agents.SimpleAgents.Meander import RedMeanderAgent
from Wrappers.ChallengeWrapper2 import ChallengeWrapper2
from Agents.MainAgent import MainAgent
import random

import py_trees_devel.py_trees as py_trees
import evaluation_bt_nodes as bt_nodes
 

MAX_EPS = 1
agent_name = 'Blue'
random.seed(0)

# Behavior tree

# Build blackboard
def build_blackboard():
    blackboard = py_trees.blackboard.Client(name = "Global")
    blackboard.register_key(key = "observation", access = py_trees.common.Access.WRITE)
    blackboard.register_key(key = "action_space", access = py_trees.common.Access.WRITE)
    blackboard.register_key(key = "action", access = py_trees.common.Access.WRITE)
    #blackboard.register_key(key = "red_observation", access = py_trees.common.Access.WRITE)
    #blackboard.register_key(key = "red_action_space", access = py_trees.common.Access.WRITE)
    #blackboard.register_key(key = "red_action", access = py_trees.common.Access.WRITE)
    blackboard.register_key(key = "cyborg", access = py_trees.common.Access.WRITE)
    blackboard.register_key(key = "wrapped_cyborg", access = py_trees.common.Access.WRITE)
    blackboard.register_key(key = "agent", access = py_trees.common.Access.WRITE)
    #blackboard.register_key(key = "reward", access = py_trees.common.Access.WRITE)

    blackboard.register_key(key = "start_actions", access = py_trees.common.Access.WRITE)
    blackboard.register_key(key = "scan_state", access = py_trees.common.Access.WRITE)
    blackboard.register_key(key = "agent_loaded", access = py_trees.common.Access.WRITE)

    blackboard.register_key(key = "step", access = py_trees.common.Access.WRITE)
    blackboard.register_key(key = "r", access = py_trees.common.Access.WRITE)
    blackboard.register_key(key = "a", access = py_trees.common.Access.WRITE)
    blackboard.register_key(key = "test_counter", access = py_trees.common.Access.WRITE)

    return blackboard

def build_bt(agent):
    root = py_trees.composites.Sequence(name = "CAGE Challenge BT", memory = True)

    determine_action = py_trees.composites.Selector(name = "Determine Action", memory = False)
    
    setup_seq = py_trees.composites.Sequence(name = "Setup Steps", memory = True)
    setup_check = bt_nodes.SetupCheck()
    setup = bt_nodes.Setup(agent)
    setup_seq.add_children([setup_check, setup])

    main_action_seq = py_trees.composites.Sequence(name = "Main Action Steps", memory = True)

    change_strat_sel = py_trees.composites.Selector(name = "Change Strategy Selector", memory = False)
    change_strat_check = bt_nodes.ChangeStratCheck()
    change_strat_check_inv = py_trees.decorators.Inverter(name = "Inverter", child = change_strat_check)
    change_strat = bt_nodes.ChangeStrat()
    change_strat_sel.add_children([change_strat_check_inv, change_strat])

    get_ppo_action = bt_nodes.GetPPOAction()

    deploy_decoy_sel = py_trees.composites.Selector(name = "Deploy Decoy Selector", memory = False)
    deploy_decoy_check = bt_nodes.DeployDecoyCheck()
    deploy_decoy_check_inv = py_trees.decorators.Inverter(name = "Inverter", child = deploy_decoy_check)
    deploy_decoy = bt_nodes.DeployDecoy()
    deploy_decoy_sel.add_children([deploy_decoy_check_inv, deploy_decoy])

    remove_decoys_sel = py_trees.composites.Selector(name = "Remove Decoys Selector", memory = False)
    remove_decoys_check = bt_nodes.RemoveDecoysCheck()
    remove_decoys_check_inv = py_trees.decorators.Inverter(name = "Inverter", child = remove_decoys_check)
    remove_decoys = bt_nodes.RemoveDecoys()
    remove_decoys_sel.add_children([remove_decoys_check_inv, remove_decoys])

    main_action_seq.add_children([change_strat_sel, get_ppo_action, deploy_decoy_sel, remove_decoys_sel])

    determine_action.add_children([setup_seq, main_action_seq])

    execute_actions = bt_nodes.ExecuteActions()

    root.add_children([determine_action, execute_actions])

    # setup = bt_nodes.Setup(agent)
    # get_action = bt_nodes.GetAction()
    # take_action = bt_nodes.TakeAction()
    # root.add_children([setup, get_action, take_action])

    #py_trees.display.render_dot_tree(root)
    return root


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


if __name__ == '__main__':
    # File setup
    team='bt_agent'
    if exp == 'sim':
        log_file = './data/'+team+'_sim_actions_and_observations.csv'
    else:
        log_file = './data/'+team+'_emu_actions_and_observations.csv'

    with open(log_file, 'w', newline='') as file:
      writer = csv.writer(file)
      writer.writerow(['Iteration', 'Blue Action', 'Blue Observation', 'Blue Reward',
                       'Red Action', 'Red Observation', 'Red Reward'])

     

    #file_name = str(inspect.getfile(CybORG))[:-10] + '/cage-2-cardiff/Evaluation/' + f'{agent.__class__.__name__}.txt'
    #print(f'Saving evaluation results to {file_name}')i
    #with open(file_name, 'a+') as data:
    #    data.write(f'CybORG v{cyborg_version}, {scenario}, Commit Hash: {commit_hash}\n')
    #    data.write(f'author: {name}, team: {team}, technique: {name_of_agent}\n')
    #    data.write(f"wrappers: {wrap_line}\n")

    scenario = 'Scenario2'
    red_agent = B_lineAgent
    path = str(inspect.getfile(CybORG))
    path = path[:-10] + f'/Shared/Scenarios/{scenario}.yaml'
    
    
    #Initialize Emulator
    emulator = bt_nodes.initialize_emulator()
    #emulator.restore()    
    for num_steps in [10]:
        #emulator = bt_nodes.initialize_run_emulator()
        blackboard = build_blackboard()
        if exp == 'sim':
            blackboard.agent = MainAgent()
        else:
            blackboard.agent = emulator.agent
        
        blackboard.cyborg = CybORG(path, 'sim', agents={'Red': red_agent})
        blackboard.wrapped_cyborg = wrap(blackboard.cyborg,"cardiff")
        #emulator.blue_observation = emulator.wrapped_cyborg.reset()
        blackboard.observation = blackboard.wrapped_cyborg.reset()
        #emulator.blue_action_space = emulator.wrapped_cyborg.get_action_space(emulator.agent_name)
        if exp == 'sim':
            blackboard.action_space = blackboard.wrapped_cyborg.get_action_space(agent_name)
        else:
            blackboard.action_space = blackboard.wrapped_cyborg.get_action_space(emulator.agent_name)
        #emulator.red_observation = emulator.cyborg.get_observation('Red')
        #emulator.red_action_space = emulator.cyborg.get_action_space('Red')
        #emulator.red_observation=translate_intial_red_obs(emulator.red_observation)

        total_reward = []
        actions = []

        for i in range(MAX_EPS):
            IP = blackboard.cyborg.get_ip_map(agent_name)

            for red_agent in [B_lineAgent]:
                if red_agent != SleepAgent:
                    blackboard.r = []
                    blackboard.a = []
                    if exp == 'sim':
                        root = build_bt(agent)
                    else:
                        root = build_bt(emulator.agent)
                    #print(root)
                    #print(emulator.wrapped_cyborg.step_counter)
                    blackboard.test_counter = 0
                    blackboard.step = 0
                    
                    for j in range(num_steps):
                        blackboard.observation = emulator.blue_observation
                        root.tick_once()
                        print('%%'*100)
                        print('Iteration start:',j)
                        print(blackboard.action)
                        #if exp == 'sim':
                            #for keys in IP.keys():
                            #    if str(IP[keys]) in 
                        #else:
                        emulator.run_emulation(blackboard.action,log_file,j)
                        blackboard.step += 1
                        print('%%'*100)
                        print('Iteration end:',j)
                    emulator.agent.end_episode()
                    #agent.end_episode()
                    
                    total_reward.append(sum(blackboard.r))
                    actions.append(blackboard.a)
                    # observation = cyborg.reset().observation
                    blackboard.observation = blackboard.wrapped_cyborg.reset()            
                    emulator.restore()
                else:
                    total_reward.extend([0, 0])
