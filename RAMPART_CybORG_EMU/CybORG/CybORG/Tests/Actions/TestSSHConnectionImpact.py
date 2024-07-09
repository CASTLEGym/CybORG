from CybORG.Emulator.Actions.Velociraptor.SSHConnectionServerAction import SSHConnectionServerAction
from CybORG.Emulator.Actions.Velociraptor.SSHConnectionImpactAction import SSHConnectionImpactAction


credentials_file = "prog_client3.yaml"

ssh_connection_server_action = SSHConnectionServerAction(
    credentials_file=credentials_file,
    hostname="TESTDOCKER1",
    remote_hostname="172.17.0.3",
    remote_username="vagrant",
    remote_password="vagrant",
    client_port=4442,
    server_port=22,
    success_probability=1.0
)

ssh_connection_server_observation = ssh_connection_server_action.execute(None)

print(f"ssh connection server port: {ssh_connection_server_observation.connection_key}")

ssh_connection_impact_action_1 = SSHConnectionImpactAction(
    credentials_file=credentials_file,
    hostname="TESTDOCKER1",
    connection_key=ssh_connection_server_observation.connection_key,
    command="ls -l /etc"
)

ssh_connection_client_observation_1 = ssh_connection_impact_action_1.execute(None)

print(f"Output:\n{ssh_connection_client_observation_1.Stdout}")

ssh_connection_client_action_2 = SSHConnectionImpactAction(
    credentials_file=credentials_file,
    hostname="TESTDOCKER1",
    connection_key=ssh_connection_server_observation.connection_key,
    command="hostname"
)

ssh_connection_client_observation_2 = ssh_connection_client_action_2.execute(None)

print(f"Output:\n{ssh_connection_client_observation_2.Stdout}")

ssh_connection_client_action_3 = SSHConnectionImpactAction(
    credentials_file=credentials_file,
    hostname="TESTDOCKER1",
    connection_key=ssh_connection_server_observation.connection_key,
    command="CLOSE"
)

ssh_connection_client_observation_3 = ssh_connection_client_action_3.execute(None)

print(f"Output:\n{ssh_connection_client_observation_3.Stdout}")

print("foo")
