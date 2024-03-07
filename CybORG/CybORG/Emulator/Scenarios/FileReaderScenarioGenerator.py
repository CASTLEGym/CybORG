import copy
import time
from ipaddress import IPv4Network
from math import log2
from pathlib import Path
from typing import Union

import yaml

from CybORG.Emulator.Actions.Velociraptor import ClientListAction
from CybORG.Shared import Scenario
from CybORG.Shared.Scenarios.ScenarioGenerator import ScenarioGenerator


class FileReaderScenarioGenerator(ScenarioGenerator):
    """
    The FileReaderScenarioGenerator reads in a file when created and uses that file to create scenarios
    """

    default_subnet_name = "DEFAULT_SUBNET"

    agents_key = "Agents"
    all_key = "all"
    allowed_subnets_key = "AllowedSubnets"
    architecture_key = "Architecture"
    blue_team_key = "Blue"
    green_team_key = "Green"
    hostname_key = "hostname"
    hosts_key = "Hosts"
    in_key = "in"
    int_key = "INT"
    interfaces_key = "Interfaces"
    nacls_key = "NASLs"
    name_key = "name"
    os_distribution_key = "OSDistribution"
    os_type_key = "OSType"
    os_version_key = "OSVersion"
    out_key = "out"
    parent_key = "parent"
    size_key = "Size"
    starting_sessions_key = "starting_sessions"
    subnets_key = "Subnets"
    system_info_key = "System info"
    type_key = "type"
    up_key = "Up"
    username_key = "username"
    user_info_key = "User info"

    all_value = "all"
    none_value = "None"
    root_value = "root"
    velociraptor_client_value = "VelociraptorClient"
    velociraptor_server_value = "VeloServer"

    session_name_prefix = "Velo"

    ubuntu_os_type = "UBUNTU"

    last_seen_at_threshold = 5*60  # 5 MINUTES

    def setup_hosts(self, scenario_dict, client_list_observation):

        hosts = scenario_dict[self.hosts_key]

        for client in client_list_observation.get_client_list():
            os_info = client.os_info
            client_name = os_info.hostname
            architecture = os_info.machine.upper()
            os_type = os_info.system.upper()
            release = os_info.release.upper()

            self.hostname_list.append(client_name)

            last_seen_at = client.last_seen_at / 1000000    # MICROSECONDS TO SECONDS
            current_time = time.time()

            up = current_time - last_seen_at <= self.last_seen_at_threshold

            os_distribution = "UNKNOWN"
            os_version = "UNKNOWN"
            if release.startswith(self.ubuntu_os_type):
                os_distribution = self.ubuntu_os_type
                os_version = release[len(self.ubuntu_os_type) + 1]

            if client_name not in hosts:
                hosts[client_name] = {}

            client_info = hosts[client_name]

            if self.system_info_key not in client_info:
                client_info[self.system_info_key] = {}

            system_info = client_info[self.system_info_key]

            system_info.update({
                self.architecture_key: architecture,
                self.os_distribution_key: os_distribution,
                self.os_type_key: os_type,
                self.os_version_key: os_version,
                self.up_key: up
            })

    def setup_subnets(self, scenario_dict):

        if self.subnets_key not in scenario_dict:
            scenario_dict[self.subnets_key] = {}

        subnets_dict = scenario_dict[self.subnets_key]

        # FOR NOW, DEFINE A DEFAULT SUBNET
        if self.default_subnet_name not in subnets_dict:
            subnets_dict[self.default_subnet_name] = {}

        default_subnet_dict = subnets_dict[self.default_subnet_name]

        # AND PUT ALL OF THE VELOCIRAPTOR CLIENTS IN IT
        default_subnet_dict[self.hosts_key] = list(self.hostname_list)

        default_subnet_dict[self.nacls_key] = {
            self.all_key: {
                self.in_key: self.all_value,
                self.out_key: self.all_value
            },
            self.size_key: len(self.hostname_list)
        }

    def setup_agent_hosts(self, int_data):
        if self.hosts_key not in int_data:
            int_data[self.hosts_key] = {}

        hosts = int_data[self.hosts_key]
        for hostname in self.hostname_list:
            hosts.update({
                hostname: {
                    self.interfaces_key: self.all_value.capitalize(),
                    self.system_info_key: self.all_value.capitalize(),
                    self.user_info_key: self.all_value.capitalize()
                }
            })

    def setup_agent_starting_sessions(self, int_data):
        if self.starting_sessions_key not in int_data:
            int_data[self.starting_sessions_key] = []

        starting_sessions = int_data[self.starting_sessions_key]

        for hostname in self.hostname_list:
            starting_sessions.append({
                self.hostname_key: hostname,
                self.name_key: self.session_name_prefix + hostname,
                self.parent_key: self.velociraptor_server_value,
                self.type_key: self.velociraptor_client_value,
                self.username_key: self.root_value
            })

    def setup_allowed_subnets(self, team):

        if self.allowed_subnets_key not in team:
            team[self.allowed_subnets_key] = []

        allowed_subnets = team[self.allowed_subnets_key] = []
        allowed_subnets.append(self.default_subnet_name)

    def setup_int(self, team):
        if self.int_key not in team:
            team[self.int_key] = {}

        int_data = team[self.int_key]

        self.setup_agent_hosts(int_data)
        self.setup_agent_starting_sessions(int_data)

    def setup_blue_team(self, agents):

        if self.blue_team_key not in agents:
            return

        blue_team = agents[self.blue_team_key]

        self.setup_allowed_subnets(blue_team)
        self.setup_int(blue_team)

    def setup_green_team(self, agents):

        if self.green_team_key not in agents:
            return

        green_team = agents[self.green_team_key]

        self.setup_allowed_subnets(green_team)
        self.setup_int(green_team)

    def __init__(self, file_path: Union[str, Path], credentials_file: Union[str, Path]):
        """
        Args:
            file_path: this is the path to the file being used to create the scenario. The file should be in yaml format
        """
        super().__init__()

        self.file_path = file_path if isinstance(file_path, Path) else Path(file_path)
        self.credentials_file = credentials_file if isinstance(credentials_file, Path) else Path(credentials_file)

        self.hostname_list = []

        self.background = "plain_background"

        # GET THE SCENARIO DATA FROM THE FILE
        with self.file_path.open() as fIn:
            scenario_dict = yaml.load(fIn, Loader=yaml.FullLoader)

        if self.hosts_key not in scenario_dict:
            scenario_dict[self.hosts_key] = {}

        #
        # DEFINE "HOSTS" SECTION
        #
        client_list_action = ClientListAction(credentials_file)
        client_list_observation = client_list_action.execute(None)

        self.setup_hosts(scenario_dict, client_list_observation)

        #
        # PLACE TEAM DATA INTO 'team_calcs' AND 'team_agents'
        #
        agents_dict = scenario_dict['Agents']

        scenario_dict['team_calcs'] = {
            agent_name: [(agent_data['reward_calculator_type'], agent_data.get('adversary', None))]
            for agent_name, agent_data in agents_dict.items()
        }
        scenario_dict['team_agents'] = {
            agent_name: [agent_name]
            for agent_name in agents_dict.keys()
        }

        # TEAM IS SAME AS AGENT NAME
        for agent_name in scenario_dict["Agents"].keys():
            agents_dict[agent_name]["team"] = agent_name

        #
        # DEFINE SUBNETS
        #
        self.setup_subnets(scenario_dict)

        #
        # AGENTS SHOULD BE PREDEFINED
        #
        if self.agents_key in scenario_dict:
            agents = scenario_dict[self.agents_key]

            self.setup_blue_team(agents)
#            self.setup_green_team(agents)  # NOT COMPLETE AND SHOULD PROBABLY BE DETERMINED FROM VELOCIRAPTOR


        # print(scenario_dict)
        scenario = Scenario.load(scenario_dict)

        # print('scenario is:',scenario)
        # add in subnet routers as hosts

        # ADDS ROUTERS -- THIS SHOULD BE DONE AUTOMATICALLY WHEN USING VELOCIRAPTOR
        # for subnet in scenario.subnets.keys():
        #     scenario.hosts[subnet+'_router'] = ScenarioHost(
        #         subnet + '_router',
        #         system_info={
        #             'OSType': 'linux',
        #             "OSDistribution": 'RouterLinux',
        #             # TODO replace with correct distro
        #             "OSVersion": "unknown",
        #             "Architecture": "unknown"
        #         },
        #         respond_to_ping=False
        #     )
        #     scenario.subnets[subnet].hosts.append(subnet+'_router')

        # SCENARIO-SPECIFIC MODS -- SKIP FOR NOW
        # if 'Scenario1b' in self.file_path or 'Scenario2' in self.file_path:
        #     scenario.operational_firewall = True
        #     for agent_name, agent_data in scenario.agents.items():
        #         if 'blue' in agent_name.lower():
        #             agent_data.default_actions = (Monitor, {'session': 0, 'agent': agent_name})
        #         else:
        #             agent_data.internal_only = True
        #     with open(f'{cyborg_path[:-7]}/render/render_data_old_scenario.json', 'r') as f:
        #         data = json.load(f)
        #     for host in scenario.hosts:
        #         scenario.hosts[host].starting_position = (data['drones'][host]['x'], data['drones'][host]['y'])

        self.scenario = scenario

    def create_scenario(self, np_random) -> Scenario:
        #pprint(self.scenario)
        #pprint(dir(self.scenario))
        scenario = copy.deepcopy(self.scenario)

        count = 0
        # randomly generate subnets cidrs for all subnets in scenario and IP addresses for all hosts in those subnets
        # and create Subnet objects using fixed size subnets (VLSM maybe viable alternative if required)
        maximum_subnet_size = max([scenario.get_subnet_size(subnet_name) for subnet_name in scenario.subnets])
        subnets_cidrs = np_random.choice(
            list(IPv4Network("10.0.0.0/16").subnets(new_prefix=32 - max(int(log2(maximum_subnet_size + 5)), 4))),
            len(scenario.subnets), replace=False)

        # allocate ip addresses and cidrs to interfaces and subnets
        for subnet_name in scenario.subnets:
            # select subnet cidr
            subnet_prefix = 32 - max(int(log2(scenario.get_subnet_size(subnet_name) + 5)), 4)
            subnet_cidr = np_random.choice(list(subnets_cidrs[count].subnets(new_prefix=subnet_prefix)))
            count += 1
            scenario.subnets[subnet_name].cidr = subnet_cidr

            # allocate ip addresses within that subnet
            ip_address_selection = np_random.choice(list(subnet_cidr.hosts()), len(scenario.get_subnet_hosts(subnet_name)), replace=False)
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
        return f"{self.file_path}"
