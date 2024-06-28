from CybORG.Emulator.Actions.RestoreAction import RestoreAction
import argparse


parser = argparse.ArgumentParser()

parser.add_argument("-u", "--user",type=str,default="dummy", help="user name")
parser.add_argument("-p", "--password",type=str,default="dummy", help="password")

args = parser.parse_args()

#DO it via arg parser
user_name=args.user
password= args.password

vms=["user-host-1","user-host-2","user-host-3","user-host-4","user-host-5","ent-server-0","ent-server-1","ent-server-2","ops-server","ops-host-1","ops-host-2","ops-host-3"]

for vm in  vms:
  print(f"resetting VM: {vm} .... ")
  restore_action = RestoreAction(
    hostname=vm,
    auth_url='https://cloud.isislab.vanderbilt.edu:5000/v3',
    project_name='mvp1',
    username=user_name,
    password=password,
    user_domain_name='ISIS',
    project_domain_name='ISIS')

  observation=restore_action.execute(None)
  print('observation success:',observation.success)
