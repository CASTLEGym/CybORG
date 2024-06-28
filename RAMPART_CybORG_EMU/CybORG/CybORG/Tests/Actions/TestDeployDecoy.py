from CybORG.Emulator.Actions.DecoyAction import DecoyAction

deploy_decoy = DecoyAction('10.0.0.15', 'ubuntu', 'ubuntu', 'Tomcat', 443)

observation = deploy_decoy.execute(None)

print(observation.__dict__)
print("foo")
