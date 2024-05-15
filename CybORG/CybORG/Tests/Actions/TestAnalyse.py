import json
from CybORG.Emulator.Actions.Velociraptor.VerifyFilesAction import VerifyFilesAction
from CybORG.Emulator.Observations.Velociraptor import VerifyFilesObservation

credentials_file = "prog_client.yaml"

previous_verification_dict = {
"/home/vagrant/velociraptor_client_0.7.1_amd64.deb": "02c50b30aeda38a0ca219a7d5f2dc011"
}

verify_files_action = VerifyFilesAction(
    credentials_file=credentials_file,
    hostname='user-host-4',
    directory="/home/vagrant",
    previous_verification_dict=previous_verification_dict
)

verify_files_observation: VerifyFilesObservation = verify_files_action.execute(None)

string = json.dumps(verify_files_observation.get_verification_dict(), indent=4, sort_keys=True)
#print('Verify file observation:',verify_files_observation.__dict__)
print('\n-> Checksums are:',string)
print("End")
