from CybORG.Emulator.Actions.Velociraptor.ImpactAction import ImpactAction

from CybORG.Emulator.Actions.Velociraptor.PrivilegeEscalateAction import PrivilegeEscalateAction
from CybORG.Emulator.Actions.Velociraptor.ExploitAction import ExploitAction
import time

credentials_file = "/home/ubuntu/prog_client.yaml"
hostname="user0"
remote_hostname="10.10.30.20"
remote_username="ubuntu"
remote_password="ubuntu"
client_port=3406




exploit_action= ExploitAction(credentials_file,hostname,remote_hostname,remote_username,remote_password,client_port)
observation=exploit_action.execute(None)

print("Connection Key is:",observation.connection_key)
conn_key= observation.connection_key



impact_action= ImpactAction(credentials_file,hostname, conn_key)
observation= impact_action.execute(controller='sc',attack='dos',duration=30,f_value=None,local_controller='lc1')
print('Impact success is:',observation.success)
print('attack id is:',observation.attack_id)
print('pid is:',observation.pid)
print('*** sleeping ***')
time.sleep (30)
killed=impact_action.kill_attack(observation.pid)
print('Killing  output is:',killed.success)

print('!! Cleaning mess, just for this testing, in real action cleaning need to be done by Blue Agent!!')
cleaned= exploit_action.run_command("CLOSE")
print('!!cleaned and connection',cleaned,'!!')











