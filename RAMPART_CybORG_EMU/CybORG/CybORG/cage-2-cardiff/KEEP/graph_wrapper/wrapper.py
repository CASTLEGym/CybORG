# Cybermonic CASTLE KEEP Agent
# Copyright (C) 2024 Cybermonic LLC

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import torch
from CybORG.Agents.Wrappers.BlueTableWrapper import BlueTableWrapper
from CybORG.Agents.Wrappers.ChallengeWrapper import ChallengeWrapper
from CybORG.Agents.Wrappers.EnumActionWrapper import EnumActionWrapper
from CybORG.Agents.Wrappers.OpenAIGymWrapper import OpenAIGymWrapper
from CybORG.Shared.Actions import *

from graph_wrapper.observation_graph import ObservationGraph

class GraphWrapper(ChallengeWrapper):
    def __init__(self, agent_name: str, env, agent=None, reward_threshold=None, max_steps=None):
        super().__init__(agent_name, env, agent, reward_threshold, max_steps)
        self.agent_name = agent_name

        # Need to keep the original environment before wrapping it
        self.original_env = env
        env = BlueTableWrapper(env, output_mode='vector')

        # Need to keep track of some intermediate variables
        env = EnumActionWrapper(env)
        env.get_action_space('Blue')
        self.possible_actions = env.possible_actions

        env = OpenAIGymWrapper(agent_name=agent_name, env=env)

        self.graph = ObservationGraph()

        self.env = env
        self.action_space = self.env.action_space
        self.observation_space = self.env.observation_space
        self.reward_threshold = reward_threshold
        self.max_steps = max_steps
        self.step_counter = None
        self.last_obs = None

    def step(self, action=None, include_names=False, include_success=False):
        # Gets the info from the tabular wrapper (4 dims per host, in order)
        obs, reward, done, info = super().step(action)

        # Tell ObservationGraph what happened and update
        action = Sleep() if action is None else self.possible_actions[action]
        dict_obs = self.original_env.get_observation(self.agent_name)
        success = dict_obs.get('success', 'UNK')
        self.graph.parse_observation(action, dict_obs)

        # Get graph data/update the state of the graph
        resp = self.graph.get_state(include_names=include_names)
        if include_names:
            x,ei,names = resp
        else:
            x,ei = resp

        x = self._combine_data(x, obs)
        self.last_obs = (x,ei)

        if include_names:
            if include_success:
                return (x,ei,names), reward, done, info, str(success)
            else:
                return (x,ei,names), reward, done, info

        return (x,ei), reward, done, info

    def reset(self):
        tab_x = super().reset()
        self.graph = ObservationGraph()
        self.graph.setup(self.original_env.get_observation('Blue'))
        graph_x, ei = self.graph.get_state()

        x = self._combine_data(graph_x, tab_x)
        self.last_obs = (x,ei)
        return x, ei

    def _combine_data(self, graph_x, tabular_x):
        tabular_x = tabular_x.reshape(tabular_x.shape[0]//4, 4)

        additional_data = torch.zeros(graph_x.size(0), 4)
        additional_data[graph_x[:,0] == 1] = torch.tensor(tabular_x, dtype=torch.float32)
        return torch.cat([graph_x, additional_data], dim=1)

    def to_action_object(self, action):
        return self.possible_actions[action]


class InductiveGraphWrapper(GraphWrapper):
    ACTIONS = [
        Analyse, Remove, DecoyApache, DecoyFemitter, DecoyHarakaSMPT, DecoySmss,
        DecoySSHD, DecoySvchost, DecoyTomcat, DecoyVsftpd, Restore,
    ]
    HOSTNAMES = [] # Filled in by self.reset()

    def action_translator(self, action):
        '''
        Unlike previous wrapper, assumes actions are indexed by
        action id rather than node id.
            E.g. actions 0,1,2 are [A_1(n_1), A_2(n_1), A_3(n_1)]
                               NOT [A_1(n_1), A_1(n_2), A_1(n_3)]

        Need to flip this back around before reusing the old code
        '''
        if action is None:
            return None

        target = action // len(self.ACTIONS)
        act = action % len(self.ACTIONS)
        act_id = act * len(self.HOSTNAMES) + target + 2
        return act_id

    def step(self, action=None, include_names=False, include_success=False):
        action = self.action_translator(action)
        return super().step(action, include_names, include_success)

    def reset(self):
        ret = super().reset()
        self.HOSTNAMES = self.graph.hostnames
        return ret

    def to_action_object(self, action):
        act_id = self.action_translator(action)
        return super().to_action_object(act_id)
