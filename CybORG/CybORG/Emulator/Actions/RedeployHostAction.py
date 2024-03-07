from typing import Union

from CybORG.Shared import Observation
from CybORG.Simulator.State import State

from openstack import connection
from openstack.compute.v2 import server as server_v2
from CybORG.Simulator.Actions import Action


class RedeployHostAction(Action):

    def __init__(
            self,
            hostname,
            auth_url,
            project_name,
            username,
            password,
            user_domain_name,
            project_domain_name
    ):
        super().__init__()

        self.auth_args = {
            'auth_url': auth_url,
            'project_name': project_name,
            'username': username,
            'password': password,
            'user_domain_name': user_domain_name,
            'project_domain_name': project_domain_name
        }

        self.hostname = hostname

    def execute(self, state: Union[State, None]) -> Observation:

        observation = Observation(False)

        conn = connection.Connection(**self.auth_args)

        server = conn.compute.find_server(self.hostname)

        if server is None:
            return observation

        server_dict = server.to_dict()

        flavor_name = server_dict['flavor']['name']
        flavor = conn.compute.find_flavor(name_or_id=flavor_name)
        flavor_id = flavor['id']

        image_id = server_dict['image']['id']

        mac_addresses = [
            item['OS-EXT-IPS-MAC:mac_addr']
            for value in server_dict['addresses'].values()
            for item in value
        ]
        ports = [list(conn.network.ports(mac_address=mac_address))[0] for mac_address in mac_addresses]
        network_list = [{'port': port.id} for port in ports]

        instance_id = server_dict['id']

        conn.compute.delete_server(instance_id)
        conn.compute.wait_for_delete(server_v2.Server(id=instance_id))

        reployed_instance = conn.compute.create_server(
            name=self.hostname,
            flavor_id=flavor_id,
            image_id=image_id,
            networks=network_list,
            key_name='castle-pem',
        )

        conn.compute.wait_for_server(reployed_instance)
