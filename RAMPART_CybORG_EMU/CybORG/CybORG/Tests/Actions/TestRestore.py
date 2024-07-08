from CybORG.Emulator.Actions.RestoreAction import RestoreAction
import argparse
import getpass


parser = argparse.ArgumentParser()

parser.add_argument("-u", "--user",type=str,default="dummy", help="user name")

args = parser.parse_args()

#DO it via arg parser
user_name = args.user

password = getpass.getpass()


restore_action = RestoreAction(
    hostname='user1',
    auth_url='https://cloud.isislab.vanderbilt.edu:5000/v3',
    project_name='mvp1a',
    username='vardhah',
    password='Roadies@5*',
    user_domain_name='ISIS',
    project_domain_name='ISIS'
)

observation=restore_action.execute(None)
print('observation success:',observation.success)

