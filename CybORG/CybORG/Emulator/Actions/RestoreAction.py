import json
from typing import Union

from pathlib import Path
import tempfile
import time

from CybORG.Shared import Observation
from CybORG.Simulator.State import State

from openstack import connection
from openstack.compute.v2 import server as server_v2
from CybORG.Shared.Actions import Action

import paramiko
import shutil
import time

from novaclient import client


class RestoreAction(Action):

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

        self.auth_url = auth_url
        self.password = password
        self.username = username
        self.user_domain_name = user_domain_name

        self.auth_args = {
            'auth_url': auth_url,
            'project_name': project_name,
            'username': username,
            'password': password,
            'user_domain_name': user_domain_name,
            'project_domain_name': project_domain_name
        }

        self.hostname = hostname

    collect_script_name = "collect_files.sh"
    collect_script_path = Path(Path(__file__).parent, f"Scripts/{collect_script_name}")

    restore_script_name = "restore_files.sh"
    restore_script_path = Path(Path(__file__).parent, f"Scripts/{restore_script_name}")

    temp_directory_path = Path(tempfile.mkdtemp(dir="/tmp"))
    tarfile_name = "collect_files.tgz"
    tarfile_path = Path(temp_directory_path, tarfile_name)

    collect_files_dir_name = "CollectFiles"

    @staticmethod
    def get_ssh_session(ip_address):

        ssh_session = paramiko.SSHClient()

        ssh_session.set_missing_host_key_policy(paramiko.client.AutoAddPolicy())

        session_success = False
        for ix in range(30):
            try:
                ssh_session.connect(hostname=ip_address, username='vagrant', password='vagrant')
                session_success = True
                break
            except Exception:
                # print(f"SSH connection try {ix} failed. Retrying...")
                time.sleep(1)

        if session_success:
            return ssh_session

        print("SSH session failed.")
        return None

    @classmethod
    def collect_files(cls, ssh_session):

        ssh_session.exec_command(f"rm -rf {cls.collect_files_dir_name} {cls.collect_script_name} {cls.tarfile_name}")

        sftp_client = ssh_session.open_sftp()

        sftp_client.put(str(cls.collect_script_path), cls.collect_script_name)

        ssh_session.exec_command(f"bash {cls.collect_script_name}")

        # WAIT FOR EXEC'D COMMAND TO COMPLETE
        time.sleep(5)

        sftp_client.get(cls.tarfile_name, str(cls.tarfile_path))
        sftp_client.close()

        ssh_session.exec_command(f"rm -rf {cls.collect_files_dir_name} {cls.collect_script_name} {cls.tarfile_name}")


    @classmethod
    def restore_files(cls, ssh_session):

        ssh_session.exec_command(f"rm -rf {cls.collect_files_dir_name} {cls.restore_script_name} {cls.tarfile_name}")

        sftp_client = ssh_session.open_sftp()

        sftp_client.put(str(cls.tarfile_path), cls.tarfile_name)
        sftp_client.put(str(cls.restore_script_path), cls.restore_script_name)

        sftp_client.close()

        ssh_session.exec_command(f"bash {cls.restore_script_name}")

        ssh_session.exec_command(f"rm -rf {cls.collect_files_dir_name} {cls.restore_script_name} {cls.tarfile_name}")

    @staticmethod
    def get_network_id_port_data_list_dict(conn, server):

        network_id_port_data_list_dict = {}
        for network_name, network_data in server.addresses.items():
            network = conn.network.find_network(network_name)
            port_data_list = []
            for item in network_data:
                ip_address = item['addr']
                mac_address = item["OS-EXT-IPS-MAC:mac_addr"]
                port = conn.network.ports(mac_address=mac_address)
                port_data_list.append({
                    'ip_address': ip_address,
                    'port': list(port)[0]
                })
            network_id_port_data_list_dict[network.id] = port_data_list

        return network_id_port_data_list_dict


    def execute(self, state: Union[State, None]) -> Observation:

        observation = Observation(False)

        conn = connection.Connection(**self.auth_args)

        server = conn.compute.find_server(self.hostname)

        if server is None:
            return observation

        flavor_name = server.flavor.name
        flavor = conn.compute.find_flavor(name_or_id=flavor_name)
        flavor_id = flavor.id

        image_id = server.image.id

        network_id_port_data_list_dict = self.get_network_id_port_data_list_dict(conn, server)

        ip_address_port_data_set = {
            item['ip_address']
            for value in network_id_port_data_list_dict.values()
            for item in value
        }

        if len(network_id_port_data_list_dict) == 0:
            return observation

        ssh_ip_address = list(ip_address_port_data_set)[0]

        ssh_session = self.get_ssh_session(ssh_ip_address)
        if ssh_session is None:
            return observation

        self.collect_files(ssh_session)

        ssh_session.close()

        instance_id = server.id
        conn.compute.delete_server(instance_id)
        conn.compute.wait_for_delete(server_v2.Server(id=instance_id))

        existing_port_list = conn.list_ports()

        existing_port_id_set = { existing_port.id for existing_port in existing_port_list }

        network_list = []
        new_network_id_port_data_dict = {}
        for network_id, port_data_list in network_id_port_data_list_dict.items():
            new_port_data_list = []
            include_network = True
            for port_data in port_data_list:
                port_id = port_data['port'].id
                if port_id in existing_port_id_set:
                    network_list.append({ 'port': port_id })
                    include_network = False
                else:
                    new_port_data_list.append(port_data)
            if len(new_port_data_list) > 0:
                new_network_id_port_data_dict[network_id] = new_port_data_list
                if include_network:
                    network_list.append({ 'uuid': network_id})

        redeployed_instance = conn.compute.create_server(
            auto_ip=False,
            name=self.hostname,
            flavor_id=flavor_id,
            image_id=image_id,
            networks=network_list,
            key_name='castle-control'
        )

        conn.compute.wait_for_server(server=redeployed_instance, wait=1200)

        redeployed_server = conn.compute.find_server(self.hostname)

        project_id = server.location.project.id
        nova_client = client.Client(
            version='2.1',
            username=self.username,
            password=self.password,
            project_id=project_id,
            auth_url=self.auth_url,
            user_domain_name=self.user_domain_name,
            project_domain_name="ISIS"
        )

        server_nova_client = nova_client.servers.get(redeployed_server.id)

        if len(new_network_id_port_data_dict) > 0:

            for network_id, port_data_list in new_network_id_port_data_dict.items():
                for port_data in port_data_list:
                    fixed_ip_address = port_data['ip_address']
                    server_nova_client.interface_attach(port_id=None, net_id=network_id, fixed_ip=fixed_ip_address)

        new_network_id_port_data_list_dict = self.get_network_id_port_data_list_dict(conn, redeployed_server)

        new_ip_address_port_data_dict = {
            item['ip_address']: item['port']
            for value in new_network_id_port_data_list_dict.values()
            for item in value
        }

        for ip_address, port in new_ip_address_port_data_dict.items():
            if ip_address not in ip_address_port_data_set:
                server_nova_client.interface_detach(port.id)

        ssh_session = self.get_ssh_session(ssh_ip_address)
        if ssh_session is None:
            return observation

        self.restore_files(ssh_session)

        ssh_session.close()

        shutil.rmtree(str(self.temp_directory_path))
