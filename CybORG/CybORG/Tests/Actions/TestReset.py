from CybORG.Emulator.Actions.Velociraptor.ResetAction import ResetAction


credentials_file = "prog_client2.yaml"



hostname=["user-host-1","user-host-2","user-host-3","user-host-4","user-host-5","defender",  "ent-server-0","ent-server-1","ent-server-2","ops-server","ops-host-1","ops-host-2","ops-host-3"]





reset_action = ResetAction(credentials_file)

while True:
  for host in hostname: 
    observation=reset_action.execute(host)

    print('Success is:',observation.success)
    print('md5 chksum are:',observation.md5)
