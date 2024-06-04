from CybORG.Emulator.Actions.Velociraptor.DiscoverNetworkServicesAction import DiscoverNetworkServicesAction

credentials_file = "prog_client.yaml"

discover_network_services_action = DiscoverNetworkServicesAction(
    credentials_file=credentials_file,
    hostname='TESTDOCKER1',
    ip_address='172.17.0.3'
)

observation = discover_network_services_action.execute(None)

print("foo")