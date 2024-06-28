from CybORG.Emulator.Actions.Velociraptor import ClientListAction

credentials_file = "prog_client.yaml"

client_list_action = ClientListAction(
    credentials_file=credentials_file,
)

client_list_observation = client_list_action.execute(None)

print("foo")
