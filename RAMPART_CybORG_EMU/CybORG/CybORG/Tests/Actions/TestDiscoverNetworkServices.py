from CybORG.Emulator.Actions.Velociraptor.DiscoverNetworkServicesAction import DiscoverNetworkServicesAction

credentials_file = "prog_client.yaml"

discover_network_services_action = DiscoverNetworkServicesAction(
    credentials_file=credentials_file,
    hostname='user-host-1',
    ip_address='10.10.10.13'
)

observation = discover_network_services_action.execute(None)
print('success is:',observation.success)
print('Port list is:',observation.port_list)
print("foo")
