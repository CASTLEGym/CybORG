import copy
import inspect
from pprint import pprint
from typing import Union
import time
from CybORG.Agents.SimpleAgents import BaseAgent
from CybORG.Agents.Wrappers import BaseWrapper
from CybORG.Shared import Results
import os
import json

class EnumActionWrapper(BaseWrapper):
    def __init__(self, env: Union[type, BaseWrapper] = None, agent: BaseAgent = None):
        super().__init__(env, agent)
        self.possible_actions = None
        self.action_signature = {}
        self.get_action_space('Red')
        self.last_action_space=None

    def step(self, agent=None, action: int = None) -> Results:
        #print("In Enumwrapper,Agent is:",agent)

        #time.sleep(2)
        # print('Possible Actions is ',self.possible_actions, 'action is:',action)
        if action is not None:
            action = self.possible_actions[action]
        print('In Enum wrapper, Action is ',action)
        return super().step(agent, action)

    def action_space_change(self, action_space: dict,*args) -> int:
        #print("In Enum action :")
        agent_n='dummy'
        for arg in args:
           #print("===> Arg is:",arg)
           agent_n=arg
        #print("action space is:",action_space)
        assert type(action_space) is dict, \
            f"Wrapper required a dictionary action space. " \
            f"Please check that the wrappers below the ReduceActionSpaceWrapper return the action space as a dict "
        possible_actions = []
        temp = {}
        params = ['action']
        possible_action_name=[]
        # for action in action_space['action']:
        for i, action in enumerate(action_space['action']):
            #print("i is:",i,"action is:",action)
            if action not in self.action_signature:
                self.action_signature[action] = inspect.signature(action).parameters
            param_dict = {}
            param_list = [{}]
            for p in self.action_signature[action]:
                #print("   -> p is:",p)
                if p == 'priority':
                    continue
                temp[p] = []
                if p not in params:
                    params.append(p)

                if len(action_space[p]) == 1:
                    for p_dict in param_list:
                        p_dict[p] = list(action_space[p].keys())[0]
                    #print("     pdict is:",p_dict)
                else:
                    new_param_list = []
                    for p_dict in param_list:

                        for key, val in action_space[p].items():
                            p_dict[p] = key
                            new_param_list.append({key: value for key, value in p_dict.items()})
                    param_list = new_param_list
            #print("--->Action is:",action.__name__,"its paramlist is:",param_list, "length is:",len(param_list))
            #time.sleep(0.5)
            #if self.last_action_space==p_dict:
            #    skip
            #else:
            #    print("%%"*100)
            #clearself.last_action_space=p_dict
            action_emu_dict={}
            #for p_dict in param_list:
                #print(action.__name__)
                #time.sleep(0.5)

            for p_dict in param_list:
                possible_actions.append(action(**p_dict))
                p_dict["action_name"]=action.__name__
                #print("modified p_dict is:",p_dict)
                possible_action_name.append(p_dict)
        self.possible_actions = possible_actions
        if not os.path.exists('./assets'):
             os.makedirs('./assets')
        file_path= './assets/blue_enum_action.txt'


        with open(file_path, 'w') as fp:
           for item in possible_action_name:
             # write each item on a new line
             fp.write("%s\n" % item)
           print('Done')
        #print('possible actions list is:',possible_action_name)
        #time.sleep(10)
        return len(possible_actions)
