from CybORG.Emulator.Actions.Velociraptor.RemoveAction import RemoveAction
from CybORG.Emulator.Actions.Velociraptor.ExploitAction import ExploitAction


credentials_file = "prog_client2.yaml"
hostname="user-host-1"
remote_hostname="10.10.10.13"
remote_username="vagrant"
remote_password="vagrant"
client_port=4444


exploit_action= ExploitAction(credentials_file,hostname,remote_hostname,remote_username,remote_password,client_port)
observation=exploit_action.execute(None)
print("Connection Key is:",observation.connection_key)
conn_key= observation.connection_key


remove_action = RemoveAction(credentials_file,hostname,conn_key)

observation=remove_action.execute(None)

print('Malicious file removed?:',observation.malicious_file_removed)
print('Connection Terminated?:',observation.connection_removed)
