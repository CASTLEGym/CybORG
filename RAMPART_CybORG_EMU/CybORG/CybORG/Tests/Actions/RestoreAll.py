import argparse
import getpass
from pathlib import Path
import sys

cyborg_dir = Path(Path(__file__).parent.parent.parent.parent).absolute()
print(cyborg_dir)
sys.path.append(str(cyborg_dir))

from CybORG.Emulator.Actions.RestoreAction import RestoreAction


parser = argparse.ArgumentParser()

parser.add_argument("-u", "--user", type=str, default="dummy", help="The user name for openstack (default:'dummy')")
    
parser.add_argument( "-url",type=str,default="https://cloud.isislab.vanderbilt.edu:5000/v3", help="The url for openstack (dafault: Vanderbilt's opensctack cluster")
parser.add_argument("-udn",type=str,default="ISIS", help="The user domain name for openstack (default: 'ISIS')")
parser.add_argument("-pdn",type=str,default="ISIS", help="The project domain name for openstack (default: 'ISIS')")
parser.add_argument("-pr", "--project",type=str,default="castle4", help="The project name for openstack (default: 'castle4')")



args = parser.parse_args()

#DO it via arg parser
user_name = args.user
password = getpass.getpass()

project_name = args.project
os_url = args.url
os_udn = args.udn
os_pdn = args.pdn

print('os_url:',os_url, ' os_udn:',os_udn,' ,os_pdn:',os_pdn)

vms=["user0","user1","user2","user3","user4","enterprise0","enterprise1","enterprise2","op_server0","op_host0","op_host1","op_host2"]

for vm in  vms:
  print(f"resetting VM: {vm} .... ")

  print(f"hostname = \"{vm}\"")
  print(f"auth_url = \"{os_url}\"")
  print(f"project_name = \"{project_name}\"")
  print(f"username = \"{user_name}\"")
  print(f"user_domain_name = \"{os_udn}\"")
  print(f"project_domain_name = \"{os_pdn}\"")
  print()
  restore_action = RestoreAction(
    hostname=vm,
    auth_url=os_url,
    project_name=project_name,
    username=user_name,
    password=password,
    user_domain_name=os_udn,
    project_domain_name=os_pdn,
    key_name='castle-control')

  observation=restore_action.execute(None)
  print('observation success:',observation.success)
