from CybORG.Emulator.Actions.DeployDecoyAction import DeployDecoy

deploy_decoy = DeployDecoy('172.17.0.3', 'velociraptor', 'velociraptor', 'apache', 80)

observation = deploy_decoy.execute(None)

print("foo")