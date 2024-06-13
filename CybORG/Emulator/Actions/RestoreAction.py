from typing import Union

from pathlib import Path
import tempfile

from CybORG.Shared import Observation
from CybORG.Simulator.State import State

from openstack import connection
from openstack.compute.v2 import server as server_v2
from CybORG.Shared.Actions import Action

import paramiko
import shutil
import time

from novaclient import client as novaclient


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
        self.project_name = project_name
        self.user_domain_name = user_domain_name
        self.project_domain_name = project_domain_name

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

        sftp_client = ssh_session.open_sftp()

        sftp_client.put(str(cls.collect_script_path), cls.collect_script_name)

        ssh_session.exec_command(f"bash {cls.collect_script_name}")

        # WAIT FOR EXEC'D COMMAND TO COMPLETE
        time.sleep(5)

        sftp_client.get(cls.tarfile_name, str(cls.tarfile_path))
        sftp_client.close()

    @classmethod
    def restore_files(cls, ssh_session):

        sftp_client = ssh_session.open_sftp()

        sftp_client.put(str(cls.tarfile_path), cls.tarfile_name)
        sftp_client.put(str(cls.restore_script_path), cls.restore_script_name)

        sftp_client.close()

        ssh_session.exec_command(f"bash {cls.restore_script_name}")

        ssh_session.exec_command(f"rm -rf {cls.tarfile_name}")

    @staticmethod
    def get_network_id_port_data_list_dict(conn, server):

        network_id_port_data_list_dict = {}
        for network_name, network_data in server.addresses.items():
            network_list = conn.list_networks(
                filters={
                    "name": network_name,
                    "project_id": server.location.project.id
                }
            )
            network = network_list[0]
            port_data_list = []
            for item in network_data:
                mac_address = item["OS-EXT-IPS-MAC:mac_addr"]
                port = list(conn.network.ports(mac_address=mac_address))[0]
                port_data_list.append({
                    "port_id": port.id,
                    "port_info": {
                        "admin_state_up": True,
                        'fixed_ips': port.fixed_ips,
                        'mac_address': mac_address,
                        "network_id": network.id
                    }
                })
            network_id_port_data_list_dict[network_name] = port_data_list

        return network_id_port_data_list_dict

    def execute(self, state: Union[State, None]) -> Observation:

        observation = Observation(False)

        # CONNECTION API
        conn = connection.Connection(**self.auth_args)

        # GET SERVER TO RESTORE
        server = conn.compute.find_server(self.hostname)

        # IF SERVER DOESN'T EXIST, RETURN FALSE OBSERVATION
        if server is None:
            return observation

        # GET FLAVOR ID OF SERVER
        flavor_name = server.flavor.name
        flavor = conn.compute.find_flavor(name_or_id=flavor_name)
        flavor_id = flavor.id

        # SERVER IMAGE ID
        image_id = server.image.id

        # INFO ABOUT SERVER PORTS
        network_id_port_data_list_dict = self.get_network_id_port_data_list_dict(conn, server)

        # IF THERE ARE NO PORTS, RETURN FALSE OBSERVATION
        if len(network_id_port_data_list_dict) == 0:
            return observation

        # GET SET OF ALL IP ADDRESSES OF SERVER,
        # AND LIST OF IP ADDRESSES ASSOCIATED WITH 'control' NETWORK
        server_ip_address_set = set()
        server_control_network_ip_address_list = []
        for network_name, port_data_list in network_id_port_data_list_dict.items():
            for port_data in port_data_list:
                for fixed_ip in port_data['port_info']['fixed_ips']:
                    ip_address = fixed_ip['ip_address']
                    server_ip_address_set.add(ip_address)
                    if network_name == 'control':
                        server_control_network_ip_address_list.append(ip_address)

        # GET IP ADDRESS FOR SSH CONNECTION
        ssh_ip_address = server_control_network_ip_address_list[0]

        # CREATE AN SSH SESSION WITH SERVER
        ssh_session = self.get_ssh_session(ssh_ip_address)
        if ssh_session is None:
            return observation

        # COLLECT CRITICAL FILES FROM SERVER, STORE LOCALLY ON THIS MACHINE
        self.collect_files(ssh_session)

        # CLOSE THE SESSION
        ssh_session.close()

        #
        # DELETE THE SERVER
        #
        instance_id = server.id
        conn.compute.delete_server(instance_id)

        # WAIT UNTIL SERVER IS FULLY DELETED
        conn.compute.wait_for_delete(server_v2.Server(id=instance_id))

        # GET ID'S OF ALL EXISTING PORTS TO SEE IF ANY THAT WERE ATTACHED TO THE SERVER STILL EXIST
        existing_port_list = conn.list_ports()
        existing_port_id_set = {existing_port.id for existing_port in existing_port_list}

        # COMPILE LIST OF STILL-EXISTING PORTS TO ATTACH TO RESTORED SERVER
        network_list = []
        new_network_id_port_data_dict = {}
        for network_name, port_data_list in network_id_port_data_list_dict.items():
            new_port_data_list = []
            include_network = True
            for port_data in port_data_list:
                port_id = port_data['port_id']
                # IF PORT EXISTS, PLACE IN LIST TO ATTACH TO RESTORED SERVER
                if port_id in existing_port_id_set:
                    network_list.append({'port': port_id})
                    include_network = False
                # OTHERWISE, PLACE DATA ABOUT PORT INTO LIST FOR RE-CREATION
                else:
                    port_data['port_id'] = None
                    new_port_data_list.append(port_data)
            if len(new_port_data_list) > 0:
                new_network_id_port_data_dict[network_name] = new_port_data_list
                if include_network:
                    network_list.append({ 'uuid': port_data['port_info']['network_id']})

        #
        # RESTORE THE SERVER
        #
        redeployed_instance = conn.compute.create_server(
            auto_ip=False,
            name=self.hostname,
            flavor_id=flavor_id,
            image_id=image_id,
            networks=network_list,
            key_name='castle-control'
        )
        # WAIT UNTIL SERVER FULLY RESTORED
        conn.compute.wait_for_server(server=redeployed_instance, wait=1200)

        # GET INFO ABOUT RESTORED SERVER
        restored_server = conn.compute.find_server(self.hostname)

        # GET A NOVA CLIENT
        project_id = server.location.project.id
        nova_client = novaclient.Client(
            version='2.1',
            username=self.username,
            password=self.password,
            project_id=project_id,
            auth_url=self.auth_url,
            user_domain_name=self.user_domain_name,
            project_domain_name="ISIS"
        )
        server_nova_client = nova_client.servers.get(restored_server.id)

        # IF THERE ARE PORTS TO RE-CREATE
        if len(new_network_id_port_data_dict) > 0:

            for port_data_list in new_network_id_port_data_dict.values():
                for port_data in port_data_list:
                    # RECREATE PORT USING NEUTRON
                    port = conn.create_port(
                        device_id=restored_server.id,
                        **port_data['port_info']
                    )
                    port_data['port_id'] = port.id

        # GET DATA ABOUT ALL EXISTING PORTS ON NEW SERVER
        new_network_id_port_data_list_dict = self.get_network_id_port_data_list_dict(conn, restored_server)

        new_port_id_ip_address_set_dict = {
            item['port_id']: {fixed_ip['ip_address'] for fixed_ip in item['port_info']['fixed_ips']}
            for value in new_network_id_port_data_list_dict.values()
            for item in value
        }

        for port_id, ip_address_set in new_port_id_ip_address_set_dict.items():

            remaining_ip_address_set = ip_address_set.difference(server_ip_address_set)
            if remaining_ip_address_set == ip_address_set:
                server_nova_client.interface_detach(port_id)

        ssh_session = self.get_ssh_session(ssh_ip_address)
        if ssh_session is None:
            return observation

        self.restore_files(ssh_session)

        ssh_session.close()

        shutil.rmtree(str(self.temp_directory_path))
