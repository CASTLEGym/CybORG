from CybORG.Emulator.Actions.Velociraptor.DiscoverRemoteSystemsAction import DiscoverRemoteSystemsAction

credentials_file = "prog_client2.yaml"

discover_remote_systems_action = DiscoverRemoteSystemsAction(
    credentials_file=credentials_file,
    hostname='user-host-1',
    cidr='10.10.10.10/24'
)

observation = discover_remote_systems_action.execute(None)
print('success is:',observation.success)
print('IP Address list is:',observation.ip_address_list)
print("foo")
