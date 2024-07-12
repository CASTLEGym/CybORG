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
import socket


class RestoreAction(Action):

    def __init__(
            self,
            hostname,
            auth_url,
            project_name,
            username,
            password,
            user_domain_name,
            project_domain_name,
            key_name
    ):
        super().__init__()

        self.auth_url = auth_url
        self.password = password
        self.username = username
        self.project_name = project_name
        self.user_domain_name = user_domain_name
        self.project_domain_name = project_domain_name
        self.key_name=key_name

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
            except paramiko.BadHostKeyException as bad_host_key_exception:
                print(f"SSH connection try {ix} failed: BadHostKeyException ({str(bad_host_key_exception)})")
                return None
            except paramiko.AuthenticationException as authentication_exception:
                print(f"SSH connection try {ix} failed: AuthenticationException ({str(authentication_exception)})")
                return None
            except paramiko.SSHException as ssh_exception:
                print(f"SSH connection try {ix} failed: SSHException ({str(ssh_exception)})")
            except socket.error:
                print(f"SSH connection try {ix} failed: socker.error ({str(socket.error)})")

            time.sleep(5)

        if session_success:
            return ssh_session

        print("SSH session failed.")
        return None

    @classmethod
    def collect_files(cls, ssh_session):

        sftp_client = ssh_session.open_sftp()

        max_tries = 10
        no_tries = 0
        while no_tries < max_tries:
            try:
                sftp_client.put(str(cls.collect_script_path), cls.collect_script_name)
                break
            except FileNotFoundError as fileNotFoundError:
                print(f"File not found error: {fileNotFoundError}")
                break
            except paramiko.SSHException as sshException:
                print(f"SSH error: {sshException}")
            except IOError as ioError:
                print(f"IOError: {ioError}")
            except Exception as exception:
                print(f"Unexpected exception: {exception}")

            time.sleep(1)

            no_tries += 1
            print(f"Copy {str(cls.collect_script_path)} failed on try {no_tries} out of {max_tries}")

        if no_tries >= max_tries:
            error = f"Could not copy {str(cls.collect_script_path)}"
            print(error)
            raise Exception(error)

        max_tries = 10
        no_tries = 0
        stdout = None
        while no_tries < max_tries:
            try:
                stdin, stdout, stderr = ssh_session.exec_command(f"bash {cls.collect_script_name}")
                break
            except paramiko.SSHException as sshException:
                print(f"SSH error: {sshException}")
            except Exception as exception:
                print(f"Unexpected exception: {exception}")

            time.sleep(1)

            no_tries += 1
            print(f"Exec of \"bash {cls.collect_script_name}\" failed on try {no_tries} out of {max_tries}")

        if no_tries >= max_tries:
            error = f"Could not exec \"bash {cls.collect_script_name}\""
            print(error)
            raise Exception(error)

        output = stdout.readlines()

        # WAIT FOR EXEC'D COMMAND TO COMPLETE
        time.sleep(5)

        max_tries = 10
        no_tries = 0
        while no_tries < max_tries:
            try:
                sftp_client.get(cls.tarfile_name, str(cls.tarfile_path))
                break
            except FileNotFoundError as fileNotFoundError:
                print(f"File not found error: {fileNotFoundError}")
                break
            except paramiko.SSHException as sshException:
                print(f"SSH error: {sshException}")
            except IOError as ioError:
                print(f"IOError: {ioError}")
            except Exception as exception:
                print(f"Unexpected exception: {exception}")

            time.sleep(1)

            no_tries += 1
            print(f"Retrieval of {str(cls.tarfile_name)} failed on try {no_tries} out of {max_tries}")

        if no_tries >= max_tries:
            error = f"Could not retrieve {str(cls.tarfile_name)}"
            print(error)
            raise Exception(error)

        sftp_client.close()

        return output

    @classmethod
    def restore_files(cls, ssh_session):

        sftp_client = ssh_session.open_sftp()

        max_tries = 10
        no_tries = 0
        while no_tries < max_tries:
            try:
                sftp_client.put(str(cls.tarfile_path), cls.tarfile_name)
                break
            except FileNotFoundError as fileNotFoundError:
                print(f"File not found error: {fileNotFoundError}")
                break
            except paramiko.SSHException as sshException:
                print(f"SSH error: {sshException}")
            except IOError as ioError:
                print(f"IOError: {ioError}")
            except Exception as exception:
                print(f"Unexpected exception: {exception}")

            time.sleep(1)

            no_tries += 1
            print(f"Copy {str(cls.tarfile_path)} failed on try {no_tries} out of {max_tries}")

        if no_tries >= max_tries:
            error = f"Could not copy {str(cls.tarfile_path)}"
            print(error)
            raise Exception(error)

        max_tries = 10
        no_tries = 0
        while no_tries < max_tries:
            try:
                sftp_client.put(str(cls.restore_script_path), cls.restore_script_name)
                break
            except FileNotFoundError as fileNotFoundError:
                print(f"File not found error: {fileNotFoundError}")
                break
            except paramiko.SSHException as sshException:
                print(f"SSH error: {sshException}")
            except IOError as ioError:
                print(f"IOError: {ioError}")
            except Exception as exception:
                print(f"Unexpected exception: {exception}")

            time.sleep(1)

            no_tries += 1
            print(f"Copy {str(cls.restore_script_path)} failed on try {no_tries} out of {max_tries}")

        if no_tries >= max_tries:
            error = f"Could not copy {str(cls.restore_script_path)}"
            print(error)
            raise Exception(error)

        sftp_client.close()

        max_tries = 10
        no_tries = 0
        stdout = None
        while no_tries < max_tries:
            try:
                stdin, stdout, stderr = ssh_session.exec_command(f"bash {cls.restore_script_name}")
                break
            except paramiko.SSHException as sshException:
                print(f"SSH error: {sshException}")
            except Exception as exception:
                print(f"Unexpected exception: {exception}")

            time.sleep(1)

            no_tries += 1
            print(f"Exec of \"bash {cls.restore_script_name}\" failed on try {no_tries} out of {max_tries}")

        if no_tries >= max_tries:
            error = f"Could not exec \"bash {cls.restore_script_name}\""
            print(error)
            raise Exception(error)

        # ssh_session.exec_command(f"rm -rf {cls.tarfile_name}")

        return stdout.readlines()

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
                        "network_id": network.id,
                        "security_groups": port.security_group_ids
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
                    if network_name.startswith('control'):
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
        for network_name, port_data_list in network_id_port_data_list_dict.items():
            for port_data in port_data_list:
                port_id = port_data['port_id']
                # IF PORT EXISTS, PLACE IN LIST TO ATTACH TO RESTORED SERVER
                if port_id in existing_port_id_set:
                    network_list.append({'port': port_id})
                    include_network = False
                # OTHERWISE, PLACE DATA ABOUT PORT INTO LIST FOR RE-CREATION
                else:
                    port = conn.create_port(
                        **port_data['port_info']
                    )
                    network_list.append({'port': port.id})

        #
        # RESTORE THE SERVER
        #
        redeployed_instance = conn.compute.create_server(
            auto_ip=False,
            name=self.hostname,
            flavor_id=flavor_id,
            image_id=image_id,
            networks=network_list,
            key_name=self.key_name
        )
        # WAIT UNTIL SERVER FULLY RESTORED
        conn.compute.wait_for_server(server=redeployed_instance, wait=1200)

        ssh_session = self.get_ssh_session(ssh_ip_address)
        if ssh_session is None:
            return observation

        output = self.restore_files(ssh_session)
        observation.Stdout = output

        ssh_session.close()

        #shutil.rmtree(str(self.temp_directory_path))

        observation.set_success(True)
        return observation
