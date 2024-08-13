from CybORG.Emulator.Actions.Velociraptor.MonitorAction import MonitorAction


credentials_file= "/home/ubuntu/prog_client.yaml"

monitor_action = MonitorAction(
    credentials_file=credentials_file,
    hostname='monitoring-node'
)

observation = monitor_action.execute(None)
print('success is:',observation.success)
print('IP Address list is:',observation.connection_info)
print("Done")
