import copy
import inspect
import json
from ipaddress import IPv4Network
from math import log2
from pathlib import Path
from typing import Union

import yaml

from CybORG.Shared import Scenario
from CybORG.Simulator.Actions import Monitor
from CybORG.Shared.Scenario import ScenarioHost
from CybORG.Shared.Scenarios.ScenarioGenerator import ScenarioGenerator


class FileReaderScenarioGenerator(ScenarioGenerator):
    """
    The FileReaderScenarioGenerator reads in a file when created and uses that file to create scenarios
    """
    def __init__(self, file_path: Union[str, Path]):
        """
        Args:
            file_path: this is the path to the file being used to create the scenario. The file should be in yaml format
        """
        super().__init__()
        self.background = "plain_background"
        self.file_path = file_path if isinstance(file_path, Path) else Path(file_path)

        # GET THE SCENARIO DATA FROM THE FILE
        with self.file_path.open() as fIn:
            scenario_dict = yaml.load(fIn, Loader=yaml.FullLoader)

        from CybORG import CybORG
        cyborg_path = Path(inspect.getfile(CybORG))
        images_file_path = Path(cyborg_path.parent, 'Simulator/Scenarios/scenario_files/images/')

        with Path(images_file_path, 'images.yaml').open() as fIn:
            images_dict = yaml.load(fIn, Loader=yaml.FullLoader)

        # READ IN HOSTS
        if scenario_dict is not None:

            hosts_dict = scenario_dict["Hosts"]
            for hostname, host_data in hosts_dict.items():

                host_image_name = host_data["image"]
                host_image_info = images_dict[host_image_name]

                if 'path' in host_image_info:
                    # REPLACE "image" KEY WITH DATA FROM IMAGE FILE
                    with Path(images_file_path, host_image_info['path']).with_suffix('.yaml').open() as fIn2:
                        host_data.update(yaml.load(fIn2, Loader=yaml.FullLoader).pop('Test_Host'))
                    host_data.pop('image')
                else:
                    # IF NO IMAGE FILE, IMAGE DATA IS DIRECTLY IN "images.yaml" FILE -- THIS OVERWRITES
                    # ALL OF THE HOST DATA SPECIFIED FOR THE HOST FROM THE SCENARIO FILE
                    hosts_dict[hostname] = copy.deepcopy(host_image_info)

        agents_dict = scenario_dict['Agents']

        # PLACE TEAM DATA INTO 'team_calcs' AND 'team_agents'
        scenario_dict['team_calcs'] = {
            agent_name: [(agent_data['reward_calculator_type'], agent_data.get('adversary', None))]
            for agent_name, agent_data in agents_dict.items()
        }
        scenario_dict['team_agents'] = {
            agent_name: [agent_name]
            for agent_name, agent_data in agents_dict.items()
        }

        # TEAM IS SAME AS AGENT NAME
        for agent_name in agents_dict.keys():
            agents_dict[agent_name]["team"] = agent_name

        #print(scenario_dict)
        # with Path(Path(__file__).parent, "foo").open("w") as fOut:
        #     yaml.dump(scenario_dict, fOut, indent=2)
        scenario = Scenario.load(scenario_dict)

        #print('scenario is:',scenario)
        # add in subnet routers as hosts
        for subnet in scenario.subnets.keys():
            scenario.hosts[subnet+'_router'] = ScenarioHost(
                subnet+'_router',
                system_info={
                    'OSType': 'linux',
                    "OSDistribution": 'RouterLinux',
                    # TODO replace with correct distro
                    "OSVersion": "unknown",
                    "Architecture": "unknown"
                },
                respond_to_ping=False
            )
            scenario.subnets[subnet].hosts.append(subnet+'_router')

        if self.file_path.stem == 'Scenario1b' or self.file_path.stem == 'Scenario2':
            scenario.operational_firewall = True
            for agent_name, agent_data in scenario.agents.items():
                if 'blue' in agent_name.lower():
                    agent_data.default_actions = (Monitor, {'session': 0, 'agent': agent_name})
                else:
                    agent_data.internal_only = True
            with Path(cyborg_path.parent, "render/render_data_old_scenario.json").open() as f:
                data = json.load(f)
            for host in scenario.hosts:
                scenario.hosts[host].starting_position = (data['drones'][host]['x'], data['drones'][host]['y'])
        self.scenario = scenario

    def create_scenario(self, np_random) -> Scenario:
        #pprint(self.scenario)
        #pprint(dir(self.scenario))
        scenario = copy.deepcopy(self.scenario)
        
        count = 0
        # randomly generate subnets cidrs for all subnets in scenario and IP addresses for all hosts in those subnets and create Subnet objects
        # using fixed size subnets (VLSM maybe viable alternative if required)
        maximum_subnet_size = max([scenario.get_subnet_size(i) for i in scenario.subnets])
        subnets_cidrs = np_random.choice(
            list(IPv4Network("10.0.0.0/16").subnets(new_prefix=32 - max(int(log2(maximum_subnet_size + 5)), 4))),
            len(scenario.subnets),
            replace=False
        )

        # allocate ip addresses and cidrs to interfaces and subnets
        for subnet_name in scenario.subnets:
            # select subnet cidr
            subnet_prefix = 32 - max(int(log2(scenario.get_subnet_size(subnet_name) + 5)), 4)
            subnet_cidr = np_random.choice(list(subnets_cidrs[count].subnets(new_prefix=subnet_prefix)))
            count += 1
            scenario.subnets[subnet_name].cidr = subnet_cidr

            # allocate ip addresses within that subnet
            ip_address_selection = np_random.choice(
                list(subnet_cidr.hosts()),
                len(scenario.get_subnet_hosts(subnet_name)),
                replace=False
            )
            allocated = 0
            for hostname in scenario.get_subnet_hosts(subnet_name):
                interface_name = f'eth{len(scenario.hosts[hostname].interface_info)}'
                scenario.hosts[hostname].interface_info.append({
                    "name": interface_name,
                    "ip_address": ip_address_selection[allocated],
                    "subnet": subnet_cidr,
                    'interface_type': 'wired'
                })
                if '_router' not in hostname:
                    router_name = subnet_name + '_router'
                    scenario.hosts[hostname].interface_info[-1]['data_links'] = [router_name]
                else:
                    if 'all' in scenario.subnets[subnet_name].nacls:
                        scenario.hosts[hostname].interface_info[-1]['data_links'] = [
                            s_n + '_router'
                            for s_n in scenario.subnets.keys() if s_n != subnet_name
                        ]
                    else:
                        scenario.hosts[hostname].interface_info[-1]['data_links'] = [
                            s_n + '_router'
                            for s_n in scenario.subnets[subnet_name].nacls.keys() if s_n != subnet_name
                        ]
                allocated += 1
            scenario.subnets[subnet_name].ip_addresses = ip_address_selection

        return scenario


    def __str__(self):
        return str(self.file_path.absolute())
        