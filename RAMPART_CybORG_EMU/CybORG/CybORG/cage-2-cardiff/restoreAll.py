from CybORG.Emulator.Actions.RestoreAction import RestoreAction
import argparse


parser = argparse.ArgumentParser()

parser.add_argument("-u", "--user",type=str,default="dummy", help="user name")
parser.add_argument("-p", "--password",type=str,default="dummy", help="password")
parser.add_argument("-pr", "--project",type=str,default="mvp1a", help="project name")
args = parser.parse_args()

#DO it via arg parser
user_name=args.user
password= args.password
project_name= args.project

vms=["user0","user1","user2","user3","user4","enterprise0","enterprise1","enterprise2","op-server0","op-host0","op-host1","op-host2"]

for vm in  vms:
  print(f"resetting VM: {vm} .... ")
  restore_action = RestoreAction(
    hostname=vm,
    auth_url='https://cloud.isislab.vanderbilt.edu:5000/v3',
    project_name=project_name,
    username=user_name,
    password=password,
    user_domain_name='ISIS',
    project_domain_name='ISIS')

  observation=restore_action.execute(None)
  print('observation success:',observation.success)
