from typing import Union

from xml.etree import ElementTree

from .RunProcessAction import RunProcessAction
from CybORG.Shared import Observation
from CybORG.Simulator.State import State
from ...Observations.Velociraptor.DiscoverRemoteSystemsObservation import DiscoverRemoteSystemsObservation

class DiscoverRemoteSystemsAction(RunProcessAction):

    def __init__(self, credentials_file, hostname, cidr):

        super().__init__(
            credentials_file=credentials_file,
            hostname=hostname,
            command=f"doas nmap -oX - -sn {cidr}"
        )
        self.cidr = cidr

    def execute(self, state: Union[State, None]) -> Observation:

        observation = super().execute(state)

        root = ElementTree.fromstring(observation.Stdout)

        address_element_list = root.findall(".//host/address[@addrtype='ipv4']")

        ip_address_list = []
        for address_element in address_element_list:
            ip_address_list.append(address_element.attrib.get("addr"))

        return DiscoverRemoteSystemsObservation(observation, self.cidr, ip_address_list)
