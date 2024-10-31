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

from collections import defaultdict

from pprint import pprint
import torch

from CybORG.Shared.Actions.AbstractActions import Remove, Restore, Analyse, Monitor
from CybORG.Shared.Actions.ConcreteActions import *
from CybORG.Shared.Enums import TrinaryEnum
from graph_wrapper.nodes import *

class NodeTracker:
    '''
    Just a hash map with extra steps
    '''
    def __init__(self):
        self.nid = 0
        self.mapping = dict()
        self.inv_mapping = dict()

    def __getitem__(self, node_str):
        node_str = str(node_str)
        if (nid := self.mapping.get(node_str)) is not None:
            return nid

        # Add to dict if it doesn't exist
        self.mapping[node_str] = self.nid
        self.inv_mapping[self.nid] = node_str

        self.nid += 1
        return self.mapping[node_str]

    def pop(self, node_str):
        nid = self.mapping.get(node_str, None)
        if nid:
            self.mapping.pop(node_str)
            self.inv_mapping.pop(nid)

    def get(self, node_str):
        return self.mapping.get(node_str, None)

    def id_to_str(self, nid):
        return self.inv_mapping.get(nid)


class LastAnalyzed:
    def __init__(self, hosts, halflife=10):
        self.hosts = hosts
        self.host_to_hid = {host:i for i,host in enumerate(self.hosts)}
        self.last_analyzed = torch.tensor([float('inf')] * len(hosts))
        self.halflife = halflife

    def analyze(self, host):
        self.hosts[self.host_to_hid[host]] = 0

    def decay(self):
        self.last_analyzed += 1

    def host_feats(self):
        h = self.last_analyzed.clone()
        h = torch.pow(0.5, h/self.halflife)
        return h

class ObservationGraph:
    '''
    Seems like the only nodes the blue agent ever sees are
    Systems, ports (connections), subnets, and files
    Possibly users and groups on systems could be important, but
    they don't seem to do anything or appear in file scans?
    '''
    NTYPES = {SystemNode: 0, SubnetNode: 1, ConnectionNode: 2, FileNode: 3}
    INV_NTYPES = [SystemNode, SubnetNode, ConnectionNode, FileNode]
    NTYPE_DIMS = [k(0,dict()).dim for k in INV_NTYPES]

    # one-hot vector of node type, plus whatever features that node has
    DIM = len(INV_NTYPES) + sum(NTYPE_DIMS)

    FEAT_MAP = INV_NTYPES
    for k in INV_NTYPES:
        FEAT_MAP = FEAT_MAP + k(0,dict()).labels

    # How much to offset each node type's feature
    OFFSETS = [len(INV_NTYPES)]
    for n in NTYPE_DIMS[:-1]:
        OFFSETS.append(n + OFFSETS[-1])

    # Really seems like this info should just be part of
    # the observation, but I guess the ports are known and
    # (in this scenario) don't change..
    DECOY_TO_PORT = {
        DecoyApache: 80,
        DecoyFemitter: 21,
        DecoyHarakaSMPT: 25,
        DecoySmss: 139,
        DecoySSHD: 22,
        DecoySvchost: 3389,
        DecoyTomcat: 443,
        DecoyVsftpd: 80 # Confirmed in src, but irl it's 20 and 21..
    }
    DECOYS = DECOY_TO_PORT.keys()

    def __init__(self, last_analyzed_feat=False):
        self.nids = NodeTracker()
        self.nodes = dict()
        self.last_analyzed_feat = last_analyzed_feat

    def setup(self, initial_observation: dict):
        '''
        Needs to be called before ObservationGraph object can be used.

            initial_observation (dict):
                The result of env.reset('Blue').observation
        '''
        # So pointless to include this. Just get rid of it
        succ = initial_observation.pop('success')

        # It would be nice if we could use env.get_ip_map() as input, but there
        # doesn't seem to be a way to access anything other than the initial observation
        # Luckilly, this has all the info we need to build an IP map anyway.
        # Want IPs to map to hostnames
        self.ip_map = {
            val['Interface'][0]['IP Address']:host
            for host,val in initial_observation.items()
        }

        # Build network topology graph of subnets
        edges = self.parse_initial_observation(initial_observation)
        src,dst = zip(*edges)

        # Graph of subnets doesn't change (I don't think..)
        # but connections that we see in observations do. They're transient
        self.permenant_edges = [
            list(src) + list(dst),
            list(dst) + list(src)
        ]

        self.transient_edges = [[],[]]

        # Keep track of which nodes are getting deleted when Remove is called
        self.host_to_sussy = defaultdict(list)
        self.last_analyzed = LastAnalyzed(self.host_ids)

        # Gotta put it back in case other methods need the observation
        initial_observation['success'] = succ

    def get_state(self, include_names=False):
        ei = torch.tensor([
            self.permenant_edges[0] + self.transient_edges[0],
            self.permenant_edges[1] + self.transient_edges[1]
        ])
        nids, ei = ei.unique(return_inverse=True)
        nodes = [self.nodes[n.item()] for n in nids]
        names = [self.nids.id_to_str(n.item()) for n in nids]
        ntypes = [self.NTYPES[type(n)] for n in nodes]

        x = torch.zeros(nids.size(0), self.DIM)
        for i,node in enumerate(nodes):
            # Get one-hot ntype feature
            ntype = ntypes[i]
            x[i][ntype] = 1.

            # Get multi-dim feature (if node has features)
            if node.dim:
                offset = self.OFFSETS[ntype]
                x[i][offset : offset + node.dim] = torch.from_numpy(node.get_features())

        if not include_names:
            return x,ei
        return x,ei,names


    def parse_initial_observation(self, obs):
        edges = set()
        hosts = []
        hostnames = []

        for hostname, info in obs.items():
            nid = self.nids[hostname]
            hosts.append(nid)
            hostnames.append(hostname)

            if 'Op_Server' in hostname:
                crown_jewel = True
            else:
                crown_jewel = False

            if 'Enterprise' in hostname or 'Op_Server' in hostname:
                is_server = True
            else:
                is_server = False

            self.nodes[nid] = SystemNode(nid, info['System info'], is_server, crown_jewel=crown_jewel)

            for sub in info['Interface']:
                sub = sub['Subnet']
                sub_id = self.nids[sub]
                self.nodes[sub_id] = SubnetNode(sub_id)

                edges.add((nid, sub_id))

            # TODO look for open ports

        self.host_ids = hosts
        self.hostnames = hostnames
        return edges

    def parse_observation(self, act, obs):
        success = obs.pop('success')
        self.last_analyzed.decay()

        if isinstance(act, Restore) and success == TrinaryEnum.TRUE:
            # print("Handling restore")
            # Removes all files/sessions/connections from act.hostname
            # I.e. remove all transient edges involving act.hostname
            host_id = self.nids[act.hostname]

            # Need to remove host related edges, and any ports it may
            # have opened to talk to other nodes
            host_ports = [
                k for (k,v) in self.nids.inv_mapping.items()
                if v.startswith(act.hostname) and k != host_id
            ]

            #[self.nids.pop(self.nids.inv_mapping[port_id]) for port_id in host_ports]
            removed = [host_id] + host_ports

            new_edges = [[],[]]
            for i in range(len(self.transient_edges[0])):
                src = self.transient_edges[0][i]
                dst = self.transient_edges[1][i]

                if src not in removed and dst not in removed:
                    new_edges[0].append(src)
                    new_edges[1].append(dst)

            self.transient_edges = new_edges
            if act.hostname in self.host_to_sussy:
                self.host_to_sussy.pop(act.hostname)

            self.nodes[host_id].feats['sus'] = False
            self.nodes[host_id].feats['pwned'] = False

        elif isinstance(act, Remove) and success == TrinaryEnum.TRUE:
            # print("handling Remove on:" )
            # print(act.hostname)
            # Removes all suspicious sessions from act.hostname
            if act.hostname in self.host_to_sussy:
                sus_ids = self.host_to_sussy.pop()
            else:
                sus_ids = []

            host_id = self.nids[act.hostname]
            self.nodes[host_id].feats['sus'] = False

            if sus_ids:
                new_edges = [[],[]]
                for i in range(len(self.transient_edges[0])):
                    if  (src := self.transient_edges[0][i]) not in sus_ids and \
                        (dst := self.transient_edges[1][i]) not in sus_ids:

                        new_edges[0].append(src)
                        new_edges[1].append(dst)

                self.transient_edges = new_edges

        elif (isinstance(act, Analyse) and success == TrinaryEnum.TRUE):
            nid = self.nids.get(act.hostname)
            self.last_analyzed.analyze(nid)

        elif (decoy_type := type(act)) in self.DECOYS and success == TrinaryEnum.TRUE:
            # Add new process (e.g. port) to act.hostname
            host_id = self.nids[act.hostname]
            port_num = self.DECOY_TO_PORT[decoy_type]
            port_id = self.nids[f'{act.hostname}:{port_num}']

            # Add edge from port -> host representing external communication
            # being allowed to enter the host through this node
            self.nodes[port_id] = ConnectionNode(port_id, is_decoy=True)
            self.transient_edges[0].append(port_id)
            self.transient_edges[1].append(host_id)


        edges = set()
        for hostname,info in obs.items():
            host_id = self.nids[hostname]

            # Observation for Monitor, Sleep, or sometimes just passively given regardless
            if (procs := info.get('Processes')):
                for proc in procs:
                    conn = proc.get('Connections')
                    if conn is None:
                        continue

                    if len(conn) > 1:
                        print("Wtf this shouldn't happen")
                        pprint(proc)
                        raise ValueError()

                    conn = conn[0]

                    # If no remote details, assume it's just an open port with
                    # no incoming comms at this time: ignore
                    # (Quirk of Vanderbilt env, but won't affect other envs)
                    if 'remote_address' not in conn or 'remote_port' not in conn:
                        continue

                    # Ignores IP addresses that aren't in the network. Workaround for
                    # Vandy emu, but shouldn't affect anything
                    if conn['remote_address'] not in self.ip_map:
                        continue

                    remote_host = self.ip_map[conn['remote_address']]
                    remote_id = self.nids[remote_host]

                    # Host is acting as a client, talking to
                    # the remote_address:remote_port
                    if conn['local_port'] > 49151:
                        port_id = self.nids[f'{remote_host}:{conn["remote_port"]}']

                        edges.update([
                            (host_id, port_id),
                            (port_id, remote_id)
                        ])

                    # Local port is the server that remote
                    # is connecting to
                    else:
                        port_id = self.nids[f'{hostname}:{conn["local_port"]}']
                        edges.update([
                            (remote_id, port_id),
                            (port_id, host_id)
                        ])

                    # Seems like this only happens if proc is suspicious?
                    # yes seems to be the case.. PID is listed, and list of Connectiosn (port 4444 metasploit shells)
                    sus = False
                    if 'PID' in proc:
                        sus = True
                        self.host_to_sussy[host_id].append(port_id)
                        self.nodes[host_id].feats['sus'] = True

                    # Just make a new node every time so we don't have to worry abt keeping
                    # track of if it's suspicious or not
                    if port_id not in self.nodes:
                        # Experiments show labeling ports as suspicious or not hurts performance (why?)
                        self.nodes[port_id] = ConnectionNode(port_id) # , suspicious_pid=sus)

            # Observation corresponding to 'Analyse'
            if (files := info.get('Files')):
                for file in files:
                    file_uq_str = f"{hostname}:{file['Path']}\\{file['File Name']}"
                    file_id = self.nids[file_uq_str]

                    self.nodes[file_id] = FileNode(file_id, file)
                    self.nodes[host_id].feats['pwned'] = True

                    edges.update([
                        (host_id, file_id),
                        (file_id, host_id)
                    ])

        if edges:
            src,dst = zip(*edges)
            self.transient_edges[0] += src
            self.transient_edges[1] += dst