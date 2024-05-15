from typing import Union

from pathlib import Path
import tempfile
import time

import json
import re
import sys

from CybORG.Shared import Observation
from CybORG.Simulator.State import State

from openstack import connection
from openstack.compute.v2 import server as server_v2
from CybORG.Shared.Actions import Action

import paramiko
import shutil
from CybORG.Emulator.Observations.RestoreObservation import RestoreObservation

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

        ssh_session.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            ssh_session.connect(hostname=ip_address, username='vagrant', password='vagrant')
        except Exception:
            print("SSH connection failed. Bailing out.")
            return None

        return ssh_session

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

    def execute(self, state: Union[State, None]) -> Observation:

        print("1")
        observation = Observation(False)

        print("2")
        conn = connection.Connection(**self.auth_args)

        print("3")
        server = conn.compute.find_server(self.hostname)

        print("4")
        if server is None:
            return observation

        
        print("5")
        server_dict = server.to_dict()

        server_json = json.dumps(server_dict, indent=5, sort_keys=True)
        print(f"server_json:\n{server_json}")

        print("6")
        flavor_name = server_dict['flavor']['name']
        flavor = conn.compute.find_flavor(name_or_id=flavor_name)
        flavor_id = flavor['id']

        print("7")
        image_id = server_dict['image']['id']

        ip_addresses = []
        network_name_list = []
        network_uuid_list = []

        print("8")
        for network, value in server_dict['addresses'].items():
            network_name_list.append(network)
            network_data = conn.network.find_network(network)
            network_uuid = network_data.id
            network_uuid_list.append({"uuid": network_uuid})
            print(f"network_data:\n{network_data}")
            for item in value:
                ip_addresses.append(item['addr'])
                
        mac_addresses = [
            item['OS-EXT-IPS-MAC:mac_addr']
            for value in server_dict['addresses'].values()
            for item in value
        ]
        ports = [list(conn.network.ports(mac_address=mac_address))[0] for mac_address in mac_addresses]
        network_list = [{'port': port.id} for port in ports]

        bar = conn.list_networks()

        print(f"list networks:\n{bar}")


        instance_id = server_dict['id']

        print("9")
        ip_address = None
        break_loop = False
        for port in ports:
            fixed_ips = port.fixed_ips
            for fixed_ip in fixed_ips:
                ip_address = fixed_ip.get("ip_address", None)
                if ip_address is not None and str(ip_address).startswith("10.0.0"):
                    break_loop = True
                    break
            if break_loop:
                break

        if ip_address is None:
            return observation

        print("10")
        print(ip_address)
        ssh_session = self.get_ssh_session(ip_address)
        if ssh_session is None:
            return observation

        print("11")
        self.collect_files(ssh_session)

        print("12")
        ssh_session.close()

        if len(ip_addresses) == 1:
            ip_addresses = ip_addresses[0]

        print(f"hostname     = {self.hostname}")
        print(f"flavor_id    = {flavor_id}")
        print(f"image_id     = {image_id}")
        print(f"networks     = {network_uuid_list}")
        print(f"ip_addresses = {ip_addresses}")

        print("13")
        conn.compute.delete_server(instance_id)
        conn.compute.wait_for_delete(server_v2.Server(id=instance_id))

        print("14")

#        ip_address_pattern = re.compile("(\\d+)\\.(\\d+)\\.(\\d)\\.(\\d+)")
#        new_ips = []
#        for ip in ip_addresses:
#            match = ip_address_pattern.search(ip)
#            n1 = int(match.group(1))
#            n2 = int(match.group(2))
#            n3 = int(match.group(3))
#            n4 = int(match.group(4)) + 1
#            
#            new_ip = f"{n1}.{n2}.{n3}.{n4}"
#
#            new_ips.append(new_ip)
#
#
#        print(f"new_ips   = {new_ips}")


        reployed_instance = conn.compute.create_server(
            name=self.hostname,
            flavor_id=flavor_id,
            image_id=image_id,
            ips=ip_addresses,
            networks=network_uuid_list,
            key_name='castle-control',
            wait=True
        )

#        print("15")
#        conn.compute.wait_for_server(reployed_instance)
#
#        print("16")
#        ssh_session = self.get_ssh_session(ip_address)
#        if ssh_session is None:
#            return observation
#
#        print("17")
#        self.restore_files(ssh_session)
#
#        print("18")
#        ssh_session.close()
#
#        print("19")
#        shutil.rmtree(str(self.temp_directory_path))
        return RestoreObservation(True)
