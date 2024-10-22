import json
from CybORG.Emulator.Actions.Velociraptor.FetchInitialObservationAction import FetchInitialObservationAction

credentials_file = "/home/ubuntu/prog_client.yaml"
host= 'user0'

fetch_intial_obs_action = FetchInitialObservationAction(credentials_file=credentials_file)

observation = fetch_intial_obs_action.execute(host)

print(observation.Stdout)
print("foo")
