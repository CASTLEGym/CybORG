# import json

from CybORG.Emulator.Actions.Velociraptor.KnownHostsAction import KnownHostsAction

credentials_file = "prog_client.yaml"

known_hosts_action = KnownHostsAction(
    credentials_file=credentials_file,
    hostname="TESTDOCKER1"
)

known_hosts_observation = known_hosts_action.execute(None)

print("foo")