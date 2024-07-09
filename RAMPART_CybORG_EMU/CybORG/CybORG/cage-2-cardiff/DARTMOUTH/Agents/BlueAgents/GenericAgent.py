import copy

from .PPOAgent import PPOAgent
import numpy as np
import os

class GenericAgent(PPOAgent):
    def __init__(self, model_dir, model_file="model.pth"):
        self.model_dir = model_dir
        self.model_file = model_file
        self.action_space = [133, 134, 135, 139, 3, 4, 5, 9, 16, 17, 18, 22, 11, 12, 13, 14, 141, 142, 143, 144,
                             132, 2, 15, 24, 25, 26, 27]
        self.end_episode()

    def get_action(self, observation, action_space=None):
        action = None
        # keep track of scans
        old_scan_state = copy.copy(self.scan_state)
        super().add_scan(observation)
        # start actions
        if len(self.start_actions) > 0:
            action = self.start_actions[0]
            self.start_actions = self.start_actions[1:]

        # load agent based on fingerprint
        elif self.agent_loaded is False:
            self.agent = self.load_generic()

            self.agent_loaded = True
            # add decoys and scan state
            self.agent.current_decoys = {1000: [55], # enterprise0
                                         1001: [], # enterprise1
                                         1002: [], # enterprise2
                                         1003: [], # user1
                                         1004: [51, 116], # user2
                                         1005: [], # user3
                                         1006: [], # user4
                                         1007: [], # defender
                                         1008: []} # opserver0
            # add old since it will add new scan in its own action (since recieves latest observation)
            self.agent.scan_state = old_scan_state

        # take action of agent
        if action is None:
            action = self.agent.get_action(observation)
        return action


    def load_generic(self):
        ckpt = os.path.join(os.getcwd(),"DARTMOUTH","Models",self.model_dir,self.model_file)
        return PPOAgent(52, self.action_space, restore=True, ckpt=ckpt,
                       deterministic=True, training=False)


    def end_episode(self):
        self.scan_state = np.zeros(10)
        self.start_actions = [51, 116, 55]
        self.agent_loaded = False


