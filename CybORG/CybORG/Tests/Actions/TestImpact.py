from CybORG.Emulator.Actions.Velociraptor.ImpactAction import ImpactAction

credentials_file = "prog_client.yaml"

impact_action = ImpactAction(
    credentials_file=credentials_file,
    hostname='user-host-1',
    controller='lc1'
)

observation = impact_action.execute(None)
print('success is:',observation.success)

