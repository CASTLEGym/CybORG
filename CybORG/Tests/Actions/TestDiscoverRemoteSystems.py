from CybORG.Emulator.Actions.Velociraptor.DiscoverRemoteSystemsAction import DiscoverRemoteSystemsAction

credentials_file = "prog_client.yaml"

discover_remote_systems_action = DiscoverRemoteSystemsAction(
    credentials_file=credentials_file,
    hostname='TESTDOCKER1',
    cidr='172.17.0.2/24'
)

observation = discover_remote_systems_action.execute(None)

print(observation)
print("foo")