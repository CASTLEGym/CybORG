import json
from CybORG.Emulator.Actions.Velociraptor.VerifyFilesAction import VerifyFilesAction
from CybORG.Emulator.Observations.Velociraptor import VerifyFilesObservation

credentials_file = "prog_client.yaml"

previous_verification_dict = {
    "/root/.bash_history": "80789b9e8b7264bc96831bc60cf57ebf",
    "/root/.bashrc": "dac0124738ea320b72ea62537a9203ec",
    "/root/.profile": "d68ce7c7d7d2bb7d48aeb2f137b828e4X",
    "/root/FOOBAR.sh": "70e3474387aaf79da8e26ef9fb3fcedb",
    "/root/FOOBAR1.sh": "70e3474387aaf79da8e26ef9fb3fcedb",
    "/root/FOOBAR2.sh": "70e3474387aaf79da8e26ef9fb3fcedb",
    "/root/killProcessListing.txt": "f2ee8bc927465bdd4af45328a21efdcdX",
    "/root/start_velociraptor_client.sh": "838c46dcc2603a98b73dff50889e887f"
}

verify_files_action = VerifyFilesAction(
    credentials_file=credentials_file,
    hostname='TESTDOCKER1',
    directory=".",
    previous_verification_dict=previous_verification_dict
)

verify_files_observation: VerifyFilesObservation = verify_files_action.execute(None)

string = json.dumps(verify_files_observation.get_verification_dict(), indent=4, sort_keys=True)

print("foo")
