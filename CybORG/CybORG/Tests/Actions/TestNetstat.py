from CybORG.Emulator.Actions.Velociraptor.NetstatAction import NetstatAction

credentials_file = "prog_client.yaml"

netstat_action = NetstatAction(
    credentials_file=credentials_file, hostname="TESTDOCKER1"
)


netstat_observation = netstat_action.execute(None)

print("foo")
