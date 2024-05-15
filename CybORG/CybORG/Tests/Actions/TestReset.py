from CybORG.Emulator.Actions.Velociraptor.ResetAction import ResetAction


credentials_file = "prog_client2.yaml"
hostname="user-host-1"



reset_action = ResetAction(credentials_file)

observation=reset_action.execute(hostname)

print('Success is:',observation.success)
print('md5 chksum are:',observation.md5)
