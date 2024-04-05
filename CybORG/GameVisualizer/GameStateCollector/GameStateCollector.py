import subprocess
import inspect
import time
import os
from copy import deepcopy
from statistics import mean, stdev
import random
import collections
from pprint import pprint
from enum import Enum
from CybORG.Agents.Wrappers.TrueTableWrapper import true_obs_to_table

class RewardTracker:
    def __init__(self):
        self.rewards = None
    def __repr__(self):
        return str({agent: dict(rewards) for agent, rewards in self.rewards.items()})
    
class GameStateCollector:
    def __init__(self):
        self.blue_agent = None
        self.red_agent = None
        self.cyborg = None
        self.num_steps = None
        self.ip_map = None
        self.host_map = None
        self.true_state = None
        self.true_table = None
        self.accumulated_rewards = collections.defaultdict(lambda: collections.defaultdict(float))
        self.game_states = collections.defaultdict(lambda: collections.defaultdict(lambda: collections.defaultdict(dict)))
        
        self.compromised_hosts = set(['User0'])
        self.exploited_hosts = set()
        self.escalated_hosts = set(['User0'])
        self.discovered_subnets = set()
        self.discovered_systems = set()

    def set_environment(self, cyborg=None, red_agent=None, blue_agent=None, num_steps=30):
        self.cyborg = cyborg
        self.blue_agent = blue_agent
        self.red_agent = red_agent
        self.num_steps= num_steps
        self._create_ip_host_maps()
        
    def _create_ip_host_maps(self):
        self.ip_map = dict(map(lambda item: (str(item[0]), item[1]), self.cyborg.environment_controller.state.ip_addresses.items()))
        self.host_map = {host: str(ip) for ip, host in self.ip_map.items()}

    def _get_true_state(self):
        return deepcopy(self.cyborg.get_agent_state('True'))

    def _get_true_state_table(self):
        self.true_state = self._get_true_state()
        return true_obs_to_table(self.true_state, self.cyborg)

    def _get_host_info(self, node):
        if '_router' in node:
            return ""

        hover_text = ""

        true_obs = self._get_true_state()
        node_info = true_obs[node]

        hover_text += "System info:<br>"
        system_info = node_info.get('System info', {})
        os_info = f"{system_info.get('OSType', '').name} " \
          f"{system_info.get('OSDistribution', '').name} " \
          f"({system_info.get('Architecture', '').name})"

        hover_text += os_info + "<br><br>"

        hover_text += "Processes info:<br>"
        
        processes = node_info.get('Processes', [])
        for proc in processes:
            process_name = proc.get('Process Name', 'N/A')
            pid = proc.get('PID', 'N/A')
            username = proc.get('Username', 'N/A')
            port_info = ', '.join([f"Port: {conn['local_port']}" for conn in proc.get('Connections', [])])
            hover_text+=f"- {process_name} (PID: {pid}, User: {username}, {port_info})<br>"

        return hover_text
        
    
    def _get_node_color(self, node):
        color = "green"
        
        if 'router' in node:
            if node in self.discovered_subnets:
                color = 'rosybrown'
        
        if node in self.discovered_systems:
            color = "pink"
        
        if node in self.escalated_hosts:
            color = "red"
            
        elif node in self.exploited_hosts:
            color = "orange"
        
        return color

    def _get_node_border(self, node, target_host=None, reset_host=None):
        if target_host and node in target_host:
            border = dict(width=2, color='black')
        elif reset_host and node in reset_host:
            border = dict(width=2, color='black')
        else:
            border = dict(width=0, color='white')
        return border

    def _get_last_reward(self, agent_type):
        return self.cyborg.get_rewards()[agent_type]

    def _update_rewards(self, agent_type, reward):
        for metric, value in reward.items():
            self.accumulated_rewards[agent_type][metric] += value

    def _get_agent_rewards(self, agent_type):
        return {metric: value for metric, value in self.accumulated_rewards[agent_type].items()}

    def get_rewards(self):
        return {agent: dict(rewards) for agent, rewards in self.accumulated_rewards.items()}
        
    def _parse_action(self, cyborg, action_str, agent, host_map, ip_map):
        action_type = action_str.split(" ")[0]
        target_host = ""
        if cyborg.get_observation(agent)['success'].__str__() == 'TRUE':
            action_str_split = action_str.split(" ")
            n = len(action_str_split)
            target_host = action_str_split[-1] if n > 1 else target_host
            # Update target host if it's an IP address to get the hostname
            target_host = ip_map.get(target_host, target_host) if target_host in ip_map else target_host
        return target_host, action_type

    def _update_host_status(self, cyborg, action_str, host_map, ip_map, host_type='Red'):
        target_host, discovered_subnet, discovered_system, exploited_host, escalated_host = None, None, None, None, None
        reset_host, remove_host, restore_host = None, None, None

        if host_type == 'Red':
            # Check Red's actions
            target_host, action_type = self._parse_action(cyborg, action_str, 'Red', host_map, ip_map)
            if target_host:
                if 'ExploitRemote' in action_type:
                    exploited_host = target_host
                elif 'PrivilegeEscalate' in action_type or 'Impact' in action_type:
                    escalated_host = target_host
                elif 'DiscoverRemoteSystems' in action_type:
                    _cidr = ".".join(target_host.split(".")[:3])
                    for ip in ip_map:
                        if _cidr in ip and 'router' in ip_map[ip]:
                            discovered_subnet = ip_map[ip]
                            target_host = discovered_subnet
                elif 'DiscoverNetworkServices' in action_type:
                    discovered_system = target_host
                    
        elif host_type == 'Blue':
            # Check Blue's actions
            reset_host, action_type = self._parse_action(cyborg, action_str, 'Blue', host_map, ip_map)
            if reset_host:
                if 'Remove' in action_type:
                    remove_host = reset_host
                elif 'Restore' in action_type:
                    restore_host = reset_host
        
        if discovered_subnet:
            self.discovered_subnets.add(discovered_subnet)

        if discovered_system:
            self.discovered_systems.add(discovered_system)
        
        if exploited_host:
            self.exploited_hosts.add(exploited_host)
            self.compromised_hosts.add(exploited_host)
        if remove_host:
            self.exploited_hosts.discard(remove_host)
            self.compromised_hosts.discard(remove_host)
        if escalated_host:
            self.escalated_hosts.add(escalated_host)
            self.compromised_hosts.add(escalated_host)
        if restore_host:
            self.escalated_hosts.discard(restore_host)
            self.compromised_hosts.discard(restore_host)
            
        return target_host, reset_host, discovered_subnet, discovered_system, exploited_host, escalated_host, remove_host, restore_host

    def _create_action_snapshot(self, action_str, host_type):
        link_diagram = self.cyborg.environment_controller.state.link_diagram
        
        action_info = {
            "action": action_str, 
            "success": self.cyborg.get_observation(host_type)['success'].__str__()
        }
        
        (
            target_host,
            reset_host,
            discovered_subnet, 
            discovered_system,
            exploited_host,
            escalated_host,
            remove_host,
            restore_host
        ) = self._update_host_status(
            self.cyborg,
            action_str,
            self.host_map,
            self.ip_map,
            host_type=host_type
        )

        node_colors = [self._get_node_color(node) for node in link_diagram.nodes]
        
        node_borders = [self._get_node_border(node, 
                                        target_host=target_host, 
                                        reset_host=reset_host) 
                        for node in link_diagram.nodes]

        host_info = [self._get_host_info(node) for node in link_diagram.nodes]

        compromised_hosts = self.compromised_hosts.copy()

        reward = self._get_last_reward(host_type)

        self._update_rewards(host_type, reward)

        sim_obs = {key: value for key, value in self.cyborg.get_observation(host_type).items() \
                   if key != 'success'}
        accu_reward = self._get_agent_rewards(host_type)
        # print(self.accumulated_rewards)
        
        action_snapshot = {
            # Populate with necessary state information
            'link_diagram': link_diagram.copy(),  # Assuming link_diagram is a NetworkX graph
            'node_colors': node_colors.copy(),
            'node_borders': node_borders.copy(),
            'compromised_hosts': compromised_hosts.copy(),
            'host_info': host_info.copy(),
            'action_info': action_info.copy(),
            'host_map': self.host_map.copy(),
            'sim_obs': sim_obs,
            'reward': reward,
            'accumulate_reward': accu_reward,
        }

        return action_snapshot
        
    def create_state_snapshot(self):
        # ... Logic to create and return a snapshot of the current game state ...
        ############
        ## fo viz ##
        ############

        state_snapshot = {}
        
        for type in ['Blue', 'Red']:
            action_str = self.cyborg.get_last_action(type).__str__()
            state_snapshot[type] = self._create_action_snapshot(action_str, type)
            
        return state_snapshot

    def update_state_snapshot(self, state_snapshot, observation):
        # @To-Do: get mininet observation involed
        for type in ['Blue', 'Red']:
            obs = observation[type]
            state_snapshot[type]['mininet_obs'] = obs
        return state_snapshot    
        
    def reset(self):
        self.compromised_hosts = set(['User0'])
        self.exploited_hosts = set()
        self.escalated_hosts = set(['User0'])
        self.discovered_subnets = set()
        self.discovered_systems = set()
        self._create_ip_host_maps()

    def store_state(self, state_snapshot, episode, step):
        self.game_states[self.num_steps][self.red_agent.__class__.__name__][episode][step] = state_snapshot.copy()

    def get_game_state(self):
        return self.game_states
