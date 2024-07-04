from typing import Union

from CybORG.Shared import Observation
from CybORG.Simulator.State import State

from CybORG.Emulator.Observations.Velociraptor.KnownHostsObservation import KnownHostsObservation
from .RunProcessAction import RunProcessAction


class KnownHostsAction(RunProcessAction):

    def __init__(self, credentials_file, hostname):

        ip_address_regex = r"[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+"
        command = f"doas sed -En '/{ip_address_regex}/s/^({ip_address_regex}).*/\\\\1/p' ~ubuntu/.ssh/known_hosts"

        super().__init__(credentials_file=credentials_file, hostname=hostname, command=command)

        self.hostname = hostname

    def execute(self, state: Union[State, None]) -> Observation:

        observation = super().execute(state)

        return KnownHostsObservation(observation)
