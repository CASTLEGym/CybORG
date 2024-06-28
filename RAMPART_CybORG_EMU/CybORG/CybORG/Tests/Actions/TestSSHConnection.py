from CybORG.Emulator.Actions.Velociraptor.SSHConnectionServerAction import SSHConnectionServerAction
from CybORG.Emulator.Actions.Velociraptor.SSHConnectionClientAction import SSHConnectionClientAction


credentials_file = "prog_client.yaml"

ssh_connection_server_action = SSHConnectionServerAction(
    credentials_file=credentials_file,
    hostname="user-host-1",
    remote_hostname="10.10.10.13",
    remote_username="vagrant",
    remote_password="vagrant",
    client_port=4444
)

ssh_connection_server_observation = ssh_connection_server_action.execute(None)

ssh_connection_client_action_1 = SSHConnectionClientAction(
    credentials_file=credentials_file,
    hostname="user-host-1",
    connection_key=ssh_connection_server_observation.connection_key,
    command="ls -l /etc"
)

ssh_connection_client_observation_1 = ssh_connection_client_action_1.execute(None)

ssh_connection_client_action_2 = SSHConnectionClientAction(
    credentials_file=credentials_file,
    hostname="user-host-1",
    connection_key=ssh_connection_server_observation.connection_key,
    command="hostname"
)

ssh_connection_client_observation_2 = ssh_connection_client_action_2.execute(None)

ssh_connection_client_action_3 = SSHConnectionClientAction(
    credentials_file=credentials_file,
    hostname="user-host-1",
    connection_key=ssh_connection_server_observation.connection_key,
    command="CLOSE"
)

ssh_connection_client_observation_3 = ssh_connection_client_action_3.execute(None)

print("foo")
