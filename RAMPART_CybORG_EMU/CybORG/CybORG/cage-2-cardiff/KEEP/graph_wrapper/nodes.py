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

from abc import ABC, abstractmethod
from collections.abc import Iterable
from collections import OrderedDict

import numpy as np

import CybORG.Shared.Enums as Enums

class Node(ABC, object):
    '''
    Ordered dict of features. Keys match CybORG output
    values are initialized to None for enums, -1 for scalars
    '''
    feats: OrderedDict

    '''
    The dimension of each of the features defined in feats
    E.g. if feats is [BooleanEnum, scaler]
    dims would be [2, 1]
    '''
    dims: Iterable[int]


    labels: list

    '''
    Defining __eq__ and __hash__ as so allows us to create a set
    of nodes to avoid duplicates later on
    '''
    def __eq__(self, other):
        if isinstance(other, Node):
            return self.uuid == other.uuid
        else:
            return False

    def __hash__(self):
        return self.uuid

    def __init__(self, uuid: int, observation: dict):
        self.uuid = uuid
        self.parse_observation(observation)


    def parse_observation(self, obs: dict) -> None:
        '''
        Given the dictionary from an observation, update/set
        features (perhaps using the set_features method)

        By default, only pulls out what can be given in an
        observation, but we have some node types with additional
        features. This method should be extended to accomidate
        '''
        for k in self.feats.keys():
            if k in obs:
                self.feats[k] = obs[k]

    def get_features(self) -> np.array:
        '''
        Convert from all the enums to a fixed size vector

        Requires the following fields to be initialized:
            self.dim: The output dimension of the feature vector
            self.dims: The output dimensions of individual one-hot features (sum(dims) == dim)
            self.feats: An ordered dict of the features we want
        '''
        out = np.zeros(self.dim)

        offset = 0
        for i,feat in enumerate(self.feats.values()):
            # Enums are 1-indexed
            if feat:
                if isinstance(feat, Iterable) and not isinstance(feat, str):
                    for f in feat:
                        out[offset + (f.value-1)] = 1
                elif isinstance(feat, float):
                    out[offset] = feat
                elif isinstance(feat, bool):
                    out[offset] = float(feat)
                elif isinstance(feat, str):
                    # Only happens when processing emulated output.
                    # Feats aren't that important, so leave blank
                    out[offset] = 0
                else:
                    out[offset + (feat.value-1)] = 1

            offset += self.dims[i]

        return out

    def human_readable(self):
        human_readable = []
        for i,feat_str in enumerate(self.feats.keys()):
            if self.dims[i] > 1:
                human_readable += [f'{feat_str}-{j}' for j in range(self.dims[i])]
            else:
                human_readable.append(feat_str)

        return human_readable

    def __str__(self):
        nl='\n'; tab='\t'
        return f'''{self.__class__}-{self.uuid}\n\t{(nl+tab).join(self.human_readable())}'''

class SystemNode(Node):
    def __init__(self, uuid: int, observation: dict, is_server=False, crown_jewel=False):
        self.feats = OrderedDict(
            Architecture = None,
            OSDistro = None,
            OSType = None,
            OSVersion = None,
            OSKernelVersion = None,
            os_patches = [],
            crown_jewel=float(crown_jewel),
            user=float(not is_server),
            server=float(is_server),
            sus=False,
            pwned=False
        )

        self.dims = [
            len(Enums.Architecture.__members__),
            len(Enums.OperatingSystemDistribution.__members__),
            len(Enums.OperatingSystemType.__members__),
            len(Enums.OperatingSystemVersion.__members__),
            len(Enums.OperatingSystemKernelVersion.__members__),
            len(Enums.OperatingSystemPatch.__members__),
            1,1,1,1,1
        ]
        self.dim = sum(self.dims)

        self.labels = list(Enums.Architecture.__members__.items()) + list(Enums.OperatingSystemDistribution.__members__.items()) +list(Enums.OperatingSystemType.__members__.items()) +list(Enums.OperatingSystemVersion.__members__.items()) + list(Enums.OperatingSystemKernelVersion.__members__.items()) + list(Enums.OperatingSystemPatch.__members__.items()) + ["crown_jewel", "user", "server", "sus", "pwned"]
        super().__init__(uuid, observation)


class ProcessNode(Node):
    def __init__(self, uuid: int, observation: dict, is_new: bool = True, is_decoy: bool = False):
        self.feats = OrderedDict(
            KnownProcess=None,
            KnownPath=None,
            ProcessType=None,
            ProcessVersion=None,
            Vulnerability=None,
            Type=None, # Used for sessions only
            is_new=float(is_new),
            is_decoy=float(is_decoy),
            is_session=0.0 # Use SessionNode to change this
        )

        self.dims = [
            len(Enums.ProcessName.__members__),
            len(Enums.Path.__members__),
            len(Enums.ProcessType.__members__),
            len(Enums.ProcessVersion.__members__),
            len(Enums.Vulnerability.__members__),
            1,1
        ]
        self.dim = sum(self.dims)

        self.labels = list(Enums.ProcessName.__members__.items()) + list(Enums.Path.__members__.items()) + list(Enums.ProcessType.__members__.items()) + list(Enums.ProcessVersion.__members__.items()) + list(Enums.Vulnerability.__members__.items()) + ["is new", "is decoy"]

        super().__init__(uuid, observation)

class SessionNode(ProcessNode):
    def __init__(self, uuid: int, observation: dict, is_new: bool = True, is_decoy: bool = False):
        super().__init__(uuid, observation, is_new, is_decoy)
        self.feats['is_session'] = 1.0


class FileNode(Node):
    def __init__(self, uuid: int, observation: dict, is_new=True):
        self.feats = OrderedDict(
            [
                (s, None) for s in [
                    'Known File',
                    'Known Path',
                    'User Permissions',
                    'Group Permissions',
                    'Default Permissions'
                ]
            ],
            Version=None,
            Type=None,
            Vendor=None,

            # Additional static features
            is_new=float(is_new),

            # Will be updated if observed later
            Density= -1.,
            Signed= -1.
        )

        self.dims = [
            len(Enums.FileType.__members__),
            len(Enums.Path.__members__),
            8,8,8, # Permissions groups
            len(Enums.FileVersion.__members__),
            len(Enums.FileType.__members__),
            len(Enums.Vendor.__members__),
            1,
            1,1
        ]
        self.dim = sum(self.dims)

        self.labels = list(Enums.FileType.__members__.items()) + list(Enums.Path.__members__.items()) + ['permissions']*24 + list(Enums.FileVersion.__members__.items()) + list(Enums.FileType.__members__.items()) + list(Enums.Vendor.__members__.items()) + ['is new', 'density', 'signed']

        super().__init__(uuid, observation)


class UserNode(Node):
    def __init__(self, uuid: int, observation: dict):
        self.pwd = observation.get('Password')
        self.pwd_hash = observation.get('Password Hash')

        self.feats = OrderedDict(
            [
                ('Password Hash Type', None),
                ('Logged in', float(-1))
            ],
            pwd_changed=float(False), # Initialize to false instead of -1
            pwd_hash_changed=float(False),
        )

        self.dims = [
            len(Enums.PasswordHashType.__members__),
            1,1,1
        ]
        self.dim = sum(self.dims)

        self.labels = list(Enums.PasswordHashType.__members__.items()) + ['logged in', 'pwd changed', 'pwd hash changed']

        super().__init__(uuid, observation)


    def parse_observation(self, obs: dict) -> None:
        '''
        Modified bc we're tracking if variables have changed
        between observations (not sure how effective this is but
        may as well throw it in)
        '''
        if (pwd := obs.get('Password')) and pwd != self.pwd:
            obs['pwd_changed'] = 1.0
            self.pwd = pwd
        else:
            obs['pwd_changed'] = 0.0

        if (pwd_hash := obs.get('Password Hash')) and pwd_hash != self.pwd_hash:
            obs['pwd_hash_changed'] = 1.0
            self.pwd_hash = pwd_hash
        else:
            obs['pwd_hash_changed'] = 0.0

        return super().parse_observation(obs)

class InterfaceNode(Node):
    '''
    No features
    '''
    feats = OrderedDict()
    dims = []
    dim = 0

    def __init__(self, uuid: int, observation: dict=dict()):
        '''
        No need to provide input dict (but just in case keep it optional)
        '''
        self.uuid = uuid

class SubnetNode(InterfaceNode):
    '''
    Same thing as Interface: no features
    '''
    def __init__(self, uuid: int, observation: dict = dict()):
        self.labels = []
        super().__init__(uuid, observation)

class GroupNode(Node):
    def __init__(self, uuid: int, observation: dict):
        self.feats = OrderedDict(
            [('Builtin Group', None)],
        )
        self.dims = [len(Enums.BuiltInGroups.__members__)]
        self.dim = self.dims[0]

        super().__init__(uuid, observation)


class ConnectionNode(Node):
    def __init__(self, uuid: int, observation: dict=None, suspicious_pid: bool=False, is_decoy: bool=False):
        self.feats = OrderedDict(
            suspicious_pid=float(suspicious_pid),
            is_decoy=float(is_decoy)
        )
        self.dims = [1,1]
        self.dim = 2

        self.labels = ['suspicious pid', 'is decoy']

        super().__init__(uuid, dict())