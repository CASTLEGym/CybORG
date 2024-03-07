from CybORG.Emulator.Actions.Velociraptor import GetTextFileContentsAction

credentials_file = "prog_client.yaml"

get_file_contents_action = GetTextFileContentsAction(
    credentials_file=credentials_file, hostname="TESTDOCKER1", text_file_path="/etc/passwd"
)

text_file_contents_observation = get_file_contents_action.execute(None)

print("foo")
