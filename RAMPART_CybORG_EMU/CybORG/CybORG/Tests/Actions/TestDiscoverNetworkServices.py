from CybORG.Emulator.Actions.Velociraptor.DiscoverNetworkServicesAction import DiscoverNetworkServicesAction

credentials_file = "/home/ubuntu/prog_client.yaml"

discover_network_services_action = DiscoverNetworkServicesAction(
    credentials_file=credentials_file,
    hostname='user0',
    ip_address='10.10.10.11'
)

observation = discover_network_services_action.execute(None)
print('success is:',observation.success)
print('Port list is:',observation.port_list)
print("foo")
