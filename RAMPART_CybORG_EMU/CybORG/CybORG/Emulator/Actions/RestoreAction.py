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

        max_tries = 120
        wait_seconds = 5

        session_success = False
        for ix in range(max_tries):
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
                print(f"SSH connection try {ix} of {max_tries} failed: SSHException ({str(ssh_exception)})", flush=True)
            except socket.error:
                print(f"SSH connection try {ix} of {max_tries} failed: socker.error ({str(socket.error)})", flush=True)

            print(f"Waiting {wait_seconds} seconds to try to establish ssh session again ... ", flush=True)
            time.sleep(wait_seconds)
            print("done.", flush=True)

        if session_success:
            return ssh_session

        print("SSH session failed.")
        return None

    def collect_files(self, ssh_session):

        sftp_client = ssh_session.open_sftp()

        print(f"Attempting to copy file \"{self.collect_script_name}\" to host \"{self.hostname}\" ...")

        max_tries = 10
        no_tries = 0

        while no_tries < max_tries:
            try:
                sftp_client.put(str(self.collect_script_path), self.collect_script_name)
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
            print(f"Copy {str(self.collect_script_path)} failed on try {no_tries} out of {max_tries}")

        if no_tries >= max_tries:
            error = f"Could not copy {str(self.collect_script_path)}"
            print(error)
            raise Exception(error)

        print(f"Succeeded in copying file \"{self.collect_script_name}\" to host \"{self.hostname}\"")
        print()

        print(f"Attempting to run script \"{self.collect_script_name}\" on host \"{self.hostname}\" ...")
        stdout = ""
        stderr = ""

        max_tries = 10
        no_tries = 0

        while no_tries < max_tries:
            try:
                stdin, stdout, stderr = ssh_session.exec_command(f"bash -x {self.collect_script_name} 2>&1")
                break
            except paramiko.SSHException as sshException:
                print(f"SSH error: {sshException}")
            except Exception as exception:
                print(f"Unexpected exception: {exception}")

            time.sleep(1)

            no_tries += 1
            print(f"Exec of \"bash {self.collect_script_name}\" failed on try {no_tries} out of {max_tries}")

        if no_tries >= max_tries:
            error = f"Could not exec \"bash {self.collect_script_name}\""
            print(error)
            print("stdout:")
            print("--------------------------------------------------")
            print(stdout.readlines())
            print("--------------------------------------------------")
            print("stderr:")
            print("--------------------------------------------------")
            print(stderr.readlines())
            print("--------------------------------------------------")
            print()
            raise Exception(error)

        output = stdout.readlines()

        print(f"Successfully ran script \"{self.collect_script_name}\" on host \"{self.hostname}\".")
        print("Output is:")
        print("".join(output))
        print()

        # WAIT FOR EXEC'D COMMAND TO COMPLETE
        time.sleep(5)

        print(
            f"Attempting to retrieve file \"{self.tarfile_name}\" from host \"{self.hostname}\" "
            f"and store as \"{self.tarfile_path}\" ..."
        )

        max_tries = 10
        no_tries = 0

        while no_tries < max_tries:
            try:
                sftp_client.get(self.tarfile_name, str(self.tarfile_path))
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
            print(f"Retrieval of {str(self.tarfile_name)} failed on try {no_tries} out of {max_tries}")

        if no_tries >= max_tries:
            error = f"Could not retrieve {str(self.tarfile_name)}"
            print(error)
            raise Exception(error)

        print(
            f"Succeeded in retrieving file \"{self.tarfile_name}\" from host \"{self.hostname}\" "
            f"and storing as \"{self.tarfile_path}\"."
        )
        print()

        sftp_client.close()

        return output

    def restore_files(self, ssh_session):

        sftp_client = ssh_session.open_sftp()

        print(f"Attempting to copy file \"{self.tarfile_name}\" to host \"{self.hostname}\" ...")

        max_tries = 20
        no_tries = 0

        while no_tries < max_tries:
            try:
                sftp_client.put(str(self.tarfile_path), self.tarfile_name)
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
            print(f"Copy {str(self.tarfile_path)} failed on try {no_tries} out of {max_tries}")

        if no_tries >= max_tries:
            error = f"Could not copy {str(self.tarfile_path)}"
            print(error)
            raise Exception(error)

        print(f"Succeeded in copying file \"{self.tarfile_name}\" to host \"{self.hostname}\"")
        print()

        print(f"Attempting to copy file \"{self.restore_script_name}\" to host \"{self.hostname}\" ...")

        max_tries = 10
        no_tries = 0

        while no_tries < max_tries:
            try:
                sftp_client.put(str(self.restore_script_path), self.restore_script_name)
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
            print(f"Copy {str(self.restore_script_path)} failed on try {no_tries} out of {max_tries}")

        if no_tries >= max_tries:
            error = f"Could not copy {str(self.restore_script_path)}"
            print(error)
            raise Exception(error)

        print(f"Succeeded in copying file \"{self.restore_script_name}\" to host \"{self.hostname}\"")
        print()

        sftp_client.close()

        print(f"Attempting to run script \"{self.restore_script_name}\" on host \"{self.hostname}\" ...")
        stdout = ""
        stderr = ""

        max_tries = 10
        no_tries = 0

        while no_tries < max_tries:
            try:
                stdin, stdout, stderr = ssh_session.exec_command(f"bash {self.restore_script_name}")
                break
            except paramiko.SSHException as sshException:
                print(f"SSH error: {sshException}")
            except Exception as exception:
                print(f"Unexpected exception: {exception}")

            time.sleep(1)

            no_tries += 1
            print(f"Exec of \"bash {self.restore_script_name}\" failed on try {no_tries} out of {max_tries}")

        if no_tries >= max_tries:
            error = f"Could not exec \"bash {self.restore_script_name}\""
            print(error)
            print("stdout:")
            print("--------------------------------------------------")
            print(stdout.readlines())
            print("--------------------------------------------------")
            print("stderr:")
            print("--------------------------------------------------")
            print(stderr.readlines())
            print("--------------------------------------------------")
            print()
            raise Exception(error)

        output = stdout.readlines()

        print(f"Successfully ran script \"{self.restore_script_name}\" on host \"{self.hostname}\".")
        print("Output is:")
        print("".join(output))
        print()

        # ssh_session.exec_command(f"rm -rf {cls.tarfile_name}")

        return output

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
        print("Establinging connection to openstack ... ", end="", flush=True)
        conn = connection.Connection(**self.auth_args)
        print("done.")
        print()

        # GET SERVER TO RESTORE
        print(f"Getting info about \"{self.hostname}\" ... ", end="", flush=True)
        server = conn.compute.find_server(self.hostname)
        print("done.")
        print()

        # IF SERVER DOESN'T EXIST, RETURN FALSE OBSERVATION
        if server is None:
            print(f"Could not get info about \"{self.hostname}\".  Returning false observation.")
            print()
            return observation

        # GET FLAVOR ID OF SERVER

        flavor_name = server.flavor.name
        print(f"Getting id of flavor about \"{flavor_name}\" ... ", end="", flush=True)
        flavor = conn.compute.find_flavor(name_or_id=flavor_name)
        print("done.")
        flavor_id = flavor.id
        print(f"id of flavor \"{flavor_name}\" is \"{flavor_id}\"")
        print()


        # SERVER IMAGE ID
        image_id = server.image.id
        print(f"id of server image is \"{image_id}\"")
        print()

        # INFO ABOUT SERVER PORTS
        print(f"Getting control-network ip-address of \"{self.hostname}\" ... ", end="", flush=True)
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
        print("done.")
        print(f"Control-network ip address of \"{self.hostname}\" is \"{ssh_ip_address}\"")
        print()

        # CREATE AN SSH SESSION WITH SERVER
        print(
            f"Attempting to acquire ssh session with \"{self.hostname}\" via \"{ssh_ip_address}\" ip-address ... ",
            end="", flush=True
        )
        ssh_session = self.get_ssh_session(ssh_ip_address)
        if ssh_session is None:
            print("FAILED.")
            print("Returning False observation")
            print()
            return observation
        print("done.")
        print()

        # COLLECT CRITICAL FILES FROM SERVER, STORE LOCALLY ON THIS MACHINE
        print(f"Collecting files for \"{self.hostname}\":")
        self.collect_files(ssh_session)
        print(f"Finished collecting files for \"{self.hostname}\".")
        print()

        # CLOSE THE SESSION
        print(f"Closing ssh session for \"{self.hostname}\" ... ", end="", flush=True)
        ssh_session.close()
        print("done.")
        print()

        #
        # DELETE THE SERVER
        #
        print(f"Deleting \"{self.hostname}\" ... ", end="", flush=True)
        instance_id = server.id
        conn.compute.delete_server(instance_id)
        print("done.")
        print()

        # WAIT UNTIL SERVER IS FULLY DELETED
        print(f"Waiting for \"{self.hostname}\" to complete deletion ... ", end="", flush=True)
        conn.compute.wait_for_delete(server_v2.Server(id=instance_id))
        print("done.")
        print()

        # GET ID'S OF ALL EXISTING PORTS TO SEE IF ANY THAT WERE ATTACHED TO THE SERVER STILL EXIST
        print(f"Acquiring set of all port ids ... ", end="", flush=True)
        existing_port_list = conn.list_ports()
        existing_port_id_set = {existing_port.id for existing_port in existing_port_list}
        print("done.")
        print()
        
        deployed_port_id_set = set()

        # COMPILE LIST OF STILL-EXISTING PORTS TO ATTACH TO RESTORED SERVER
        print(f"Compiling list of port ids for \"{self.hostname}\" ... ", end="", flush=True)
        network_list = []
        for network_name, port_data_list in network_id_port_data_list_dict.items():
            for port_data in port_data_list:
                port_id = port_data['port_id']

                # IF port_id SPECIFIED MULTIPLE TIMES, SOMETHING IS WRONG
                if port_id in deployed_port_id_set:
                    print(f"WARNING:  PORT WITH ID \"{port_id}\" SPECIFIED MORE THAN ONCE -- SKIPPING")
                    continue

                # IF PORT EXISTS, PLACE IN LIST TO ATTACH TO RESTORED SERVER
                if port_id in existing_port_id_set:
                    network_list.append({'port': port_id})
                    include_network = False
                    deployed_port_id_set.add(port_id)

                # OTHERWISE, PLACE DATA ABOUT PORT INTO LIST FOR RE-CREATION
                else:
                    port = conn.create_port(
                        **port_data['port_info']
                    )
                    network_list.append({'port': port.id})
                    deployed_port_id_set.add(port.id)
        print("done.")
        print(f"Port ids compiled for \"{self.hostname}\" are:")
        print(network_list)
        print()

        #
        # RESTORE THE SERVER
        #
        print(f"Restoring \"{self.hostname}\" ... ", end="", flush=True)
        redeployed_instance = conn.compute.create_server(
            auto_ip=False,
            name=self.hostname,
            flavor_id=flavor_id,
            image_id=image_id,
            networks=network_list,
            key_name=self.key_name
        )
        print("done.")
        print()

        # WAIT UNTIL SERVER FULLY RESTORED
        print(f"Waiting for \"{self.hostname}\" to complete restore ... ", end="", flush=True)
        conn.compute.wait_for_server(server=redeployed_instance, wait=7200)
        print("done.")
        print()

        print(
            f"Attempting to acquire (another) ssh session with \"{self.hostname}\" via \"{ssh_ip_address}\" "
            "ip-address ... ",
            end="", flush=True
        )
        ssh_session = self.get_ssh_session(ssh_ip_address)
        if ssh_session is None:
            print("FAILED.")
            print("Returning False observation")
            print()
            return observation
        print("done.")
        print()

        print(f"Restoring files for \"{self.hostname}\":")
        output = self.restore_files(ssh_session)
        observation.Stdout = output
        print(f"Finished restoring files for \"{self.hostname}\".")
        print()


        ssh_session.close()

        #shutil.rmtree(str(self.temp_directory_path))

        observation.set_success(True)
        return observation
