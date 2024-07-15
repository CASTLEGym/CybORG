from typing import Union

from xml.etree import ElementTree

from .RunProcessAction import RunProcessAction
from CybORG.Shared import Observation
from CybORG.Simulator.State import State
from ...Observations.Velociraptor.DiscoverNetworkServicesObservation import DiscoverNetworkServicesObservation


class DiscoverNetworkServicesAction(RunProcessAction):

    def __init__(self, credentials_file, hostname, ip_address):

        super().__init__(
            credentials_file=credentials_file,
            hostname=hostname,
            command=f"doas nmap -oX - -p 1-1000 {ip_address}"
        )
        self.ip_address = ip_address

    def execute(self, state: Union[State, None]) -> Observation:

        observation = super().execute(state)
        print('observation dict:',observation.__dict__)
        port_list = []
        if observation.success== True:
          root = ElementTree.fromstring(observation.Stdout)
          port_element_list = root.findall(".//host/ports/port[@protocol='tcp']")
          for port_element in port_element_list:
            port_list.append(port_element.attrib.get("portid"))

          observation.set_success(True)
        return DiscoverNetworkServicesObservation(observation, self.ip_address, port_list)
