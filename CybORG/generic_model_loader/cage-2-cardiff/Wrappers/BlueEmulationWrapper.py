from copy import deepcopy
from prettytable import PrettyTable
import numpy as np
import os
import json
from enum import Enum
  
class TrinaryEnum(Enum):
    TRUE = 1
    FALSE = 0
    UNKNOWN = 2




class BlueEmulationWrapper():
    def __init__(self,host_baseline_info):
        self.baseline = host_baseline_info
        self.blue_info = {}
        self.last_action=None
        self.success= TrinaryEnum.UNKNOWN

    def reset(self, obs):
        self.blue_info = obs
        #print('\n blueEmulationwrapper, self.blue_info:',self.blue_info)	
        obs = self.observation_change(obs, baseline=True)
        print('\n In BlueEmulationwrapper, obs is:',obs)
        return obs

    def step(self, action,obs):
        print('\n=> action from blue emu wrapper, is:',action)
        print('\n-> i/p obs from blue table wraper, is:',obs)
        obs = self.observation_change(obs)
        print('\n-> o/p obs from blue_table wrapper, is:',obs)
        self.last_action=action
        return obs

    def get_table(self, output_mode='blue_table'):
        if output_mode == 'blue_table':
            return self._create_blue_table(success=None)
        elif output_mode == 'true_table':
            return self.env.get_table()

    def observation_change(self, observation, baseline=False):
        obs = observation if type(observation) == dict else observation.data
        obs = deepcopy(observation)
        success = self.success
        self._process_last_action()
        
        anomaly_obs = self._detect_anomalies(obs) if not baseline else obs
     
        info = self._process_anomalies(anomaly_obs)
        
        if baseline:
            for host in info:
                info[host][-2] = 'None'
                info[host][-1] = 'No'
                self.blue_info[host][-1] = 'No'

        self.info = info
        print('self.Info is :',self.info)
        return self._create_vector(success)
        
    

    def _process_last_action(self):
        action = self.last_action
        #print('\n \n *** last action is:',action)
        if action is not None:
            name = action.split(" ")[0]
            hostname = action.split(" ")[1] if name in ('Restore', 'Remove') else None

            if name == 'Restore':
                self.blue_info[hostname][-1] = 'No'
            elif name == 'Remove':
                compromised = self.blue_info[hostname][-1]
                if compromised != 'No':
                    self.blue_info[hostname][-1] = 'Unknown'
        print('\n-> self.blue info is:',self.blue_info)

    def _detect_anomalies(self, obs):
        #print('\n from detect anomalies, input obs is:',obs)
        if self.baseline is None:
            raise TypeError(
                'BlueTableWrapper was unable to establish baseline. This usually means the environment was not reset before calling the step method.')

        anomaly_dict = {}
        for hostid, host in obs.items():
            if hostid == 'success':
                continue

            host_baseline = self.baseline[hostid]
            print('\n=> From blue, Host id is:',hostid)
            print('--> Host is:',host)
            print('\n-> Host baseline is:',host_baseline)
            if host == host_baseline:
                continue

            host_anomalies = {}
            if 'Files' in host:
                baseline_files = host_baseline.get('Files', [])
                print('\n-> Baseline files:',baseline_files)
                anomalous_files = []
                for f in host['Files']:
                    if f not in baseline_files:
                        anomalous_files.append(f)
                #print('\n anomalous files:',anomalous_files)
                if anomalous_files:
                    host_anomalies['Files'] = anomalous_files

            if 'Processes' in host:
                
                baseline_processes = host_baseline.get('Processes', [])
                print('\n-> Baseline processes:',baseline_processes)
                anomalous_processes = []
                for p in host['Processes']:
                    if p not in baseline_processes:
                        anomalous_processes.append(p)
                if anomalous_processes:
                    host_anomalies['Processes'] = anomalous_processes
                #print('\n anomalous processes:',anomalous_processes)
            if host_anomalies:
                anomaly_dict[hostid] = host_anomalies
        print('\n anomaly dict is:',anomaly_dict)
        return anomaly_dict

    def _process_anomalies(self, anomaly_dict):
        info = deepcopy(self.blue_info)
        for hostid, host_anomalies in anomaly_dict.items():
            assert len(host_anomalies) > 0
            if 'Processes' in host_anomalies:
                # added fix
                if "Connections" in host_anomalies['Processes'][-1]:
                    connection_type = self._interpret_connections(host_anomalies['Processes'])
                    info[hostid][-2] = connection_type
                    if connection_type == 'Exploit':
                        info[hostid][-1] = 'User'
                        self.blue_info[hostid][-1] = 'User'
            if 'Files' in host_anomalies:
                malware = [f['Density'] >= 0.9 for f in host_anomalies['Files']]
                if any(malware):
                    info[hostid][-1] = 'Privileged'
                    self.blue_info[hostid][-1] = 'Privileged'

        return info

    def _interpret_connections(self, activity: list):
        #print("_interpret connections:, activity is:",activity)
        num_connections = len(activity)
        ports = set([item['Connections'][0]['local_port'] \
                     for item in activity if 'Connections' in item])
        #print('** ports are:',ports,'num of connections:',num_connections)
        port_focus = len(ports)

        remote_ports = set([item['Connections'][0].get('remote_port') \
                            for item in activity if 'Connections' in item])
        if None in remote_ports:
            remote_ports.remove(None)

        if num_connections >= 3 and port_focus >= 3:
            anomaly = 'Scan'
        elif 4444 in remote_ports:
            anomaly = 'Exploit'
        elif num_connections >= 3 and port_focus == 1:
            anomaly = 'Exploit'
        else:
            anomaly = 'Scan'

        return anomaly


    def _create_blue_table(self, success):
        table = PrettyTable([
            'Subnet',
            'IP Address',
            'Hostname',
            'Activity',
            'Compromised'
        ])
        for hostid in self.info:
            table.add_row(self.info[hostid])

        table.sortby = 'Hostname'
        table.success = success
        return table

    def _create_vector(self, success):
        table = self._create_blue_table(success)._rows
        #print('From blue table wrapper, table is:',table)
        proto_vector = []
        for row in table:
            # Activity
            activity = row[3]
            if activity == 'None':
                value = [0, 0]
            elif activity == 'Scan':
                value = [1, 0]
            elif activity == 'Exploit':
                value = [1, 1]
            else:
                raise ValueError('Table had invalid Access Level')
            proto_vector.extend(value)

            # Compromised
            compromised = row[4]
            if compromised == 'No':
                value = [0, 0]
            elif compromised == 'Unknown':
                value = [1, 0]
            elif compromised == 'User':
                value = [0, 1]
            elif compromised == 'Privileged':
                value = [1, 1]
            else:
                raise ValueError('Table had invalid Access Level')
            proto_vector.extend(value)

        return np.array(proto_vector)

    def get_attr(self, attribute: str):
        return self.env.get_attr(attribute)

    def get_observation(self, agent: str):
        if agent == 'Blue' and self.output_mode == 'table':
            output = self.get_table()
        else:
            output = self.get_attr('get_observation')(agent)

        return output

    def get_agent_state(self, agent: str):
        return self.get_attr('get_agent_state')(agent)

    def get_action_space(self, agent):
        return self.env.get_action_space(agent)

    def get_last_action(self, agent):
        return self.last_action

    def get_ip_map(self):
        return self.get_attr('get_ip_map')()

    def get_rewards(self):
        return self.get_attr('get_rewards')()
