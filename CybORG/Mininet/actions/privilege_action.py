import argparse

from CybORG.Emulator.Actions.Velociraptor.SSHConnectionServerAction import SSHConnectionServerAction
from CybORG.Emulator.Actions.Velociraptor.SSHConnectionClientAction import SSHConnectionClientAction

def parseCmdLineArgs ():
    # parse the command line
    parser = argparse.ArgumentParser ()

    # add optional arguments
    # parser.add_argument ("-ip", "--ip", default="0.0.0.0", help="IP Address")
    parser.add_argument ("-host", "--hostname", default="cpswtjustin", help="Hostname, use hostname to figure out hostname")
    parser.add_argument ("-remote", "--remote", default="0.0.0.0", help="Remote IP Address")

    # parse the args
    args = parser.parse_args ()

    return args

if __name__ == "__main__":
  
    parsed_args = parseCmdLineArgs ()
    
    # ip = parsed_args.ip
    hostname = parsed_args.hostname
    remote_ip = parsed_args.remote
    
    # print(f"At IP Address: {ip}")
    print(f"Attacker Hostname: {hostname}")
    print(f"Remote IP Address: {remote_ip}")

    credentials_file = "/etc/velociraptor/prog_client.yaml"
    
    ssh_connection_server_action = SSHConnectionServerAction(
        credentials_file=credentials_file,
        hostname=hostname,
        remote_hostname=remote_ip,
        remote_username="root",
        remote_password="1234",
        client_port=4444
    )
    
    ssh_connection_server_observation = ssh_connection_server_action.execute(None)
    
    ssh_connection_client_action_1 = SSHConnectionClientAction(
        credentials_file=credentials_file,
        hostname=hostname,
        connection_key=ssh_connection_server_observation.connection_key,
        command="ls -l /etc"
    )
    
    ssh_connection_client_observation_1 = ssh_connection_client_action_1.execute(None)
    
    ssh_connection_client_action_2 = SSHConnectionClientAction(
        credentials_file=credentials_file,
        hostname=hostname,
        connection_key=ssh_connection_server_observation.connection_key,
        command="hostname"
    )
    
    ssh_connection_client_observation_2 = ssh_connection_client_action_2.execute(None)
    
    ssh_connection_client_action_3 = SSHConnectionClientAction(
        credentials_file=credentials_file,
        hostname=hostname,
        connection_key=ssh_connection_server_observation.connection_key,
        command="CLOSE"
    )
    
    ssh_connection_client_observation_3 = ssh_connection_client_action_3.execute(None)
    
    print("foo")