from CybORG.Emulator.Actions.Velociraptor.ImpactAction import ImpactAction

credentials_file = "/home/ubuntu/prog_client.yaml"

impact_action = ImpactAction(
    credentials_file=credentials_file,
    hostname='user0',
    controller='lc1'
)

observation = impact_action.execute(None)
print('success is:',observation.success)

