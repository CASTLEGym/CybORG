from CybORG.Emulator.Actions.Velociraptor.ImpactAction import ImpactAction

from CybORG.Emulator.Actions.Velociraptor.PrivilegeEscalateAction import PrivilegeEscalateAction
from CybORG.Emulator.Actions.Velociraptor.ExploitAction import ExploitAction
import time

credentials_file = "/home/ubuntu/prog_client.yaml"
hostname="user0"
remote_hostname="10.10.30.20"
remote_username="ubuntu"
remote_password="ubuntu"
client_port=4745




exploit_action= ExploitAction(credentials_file,hostname,remote_hostname,remote_username,remote_password,client_port)
observation=exploit_action.execute(None)

print("Connection Key is:",observation.connection_key)
conn_key= observation.connection_key
"""
pes_action=PrivilegeEscalateAction(credentials_file,hostname,conn_key,remote_hostname,remote_username,remote_password,client_port)
observation=pes_action.execute(None)
print("Success is:",observation.success)
print("Current User?:",observation.user)
print("Any new host explored?:",observation.explored_host)
print("PID of malicious process?",observation.pid)
print('!!Please clean the mess after test!!')
"""


impact_action= ImpactAction(credentials_file,hostname, conn_key)
observation= impact_action.execute()
print('Impact success is:',observation.success)
print('attack id is:',observation.attack_id)
print('pid is:',observation.pid)
print('*** sleeping ***')
time.sleep (60)
killed=impact_action.kill_attack(observation.pid)
print('Killing  output is:',killed.success)

print('!! Cleaning mess, just for this testing, in real action cleaning need to be done by Blue Agent!!')
cleaned= exploit_action.run_command("CLOSE")
print('!!cleaned and connection',cleaned,'!!')











