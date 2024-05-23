import json
from CybORG.Emulator.Actions.Velociraptor.AnalyseAction import AnalyseAction
from CybORG.Emulator.Observations.Velociraptor import AnalyseObservation

credentials_file = "prog_client.yaml"

previous_verification_dict = {
    "/home/ubuntu/Tomcat": "2e0c9cca79009b53b5a0288f5cba9ace",
    "/home/ubuntu/adhoc.sh": "bccf1957d9b0767eb0021fe72a418855",
    "/home/ubuntu/cmd.sh": "c67e0b30a5440c8c52bc607d9e239a17",
    "/home/ubuntu/decoy_connections.log": "cafb0485971517dcec21dde8622235dc",
    "/home/ubuntu/densityscout": "0fa707b2ff211cf488adfe4cc937bfbf",
    "/home/ubuntu/make_ssh_connection.sh": "c1dd4e9a93ffae5bbcd775b73664b686",
    "/home/ubuntu/start_velociraptor_client.sh": "e203ac462ebb0c3680fddacd3d109c21",
    "/home/vagrant/velociraptor_client_0.7.1_amd64.deb": "02c50b30aeda38a0ca219a7d5f2dc011"
} 

verify_files_action = AnalyseAction(
    credentials_file=credentials_file,
    hostname='user-host-4',
    directory="/home/ubuntu",
    previous_verification_dict=previous_verification_dict
)

verify_files_observation: AnalyseObservation = verify_files_action.execute(None)

string = json.dumps(verify_files_observation.get_verification_dict(), indent=4, sort_keys=True)
low_density_files= verify_files_observation.get_different_checksum_file_list()
#print('Verify file observation:',verify_files_observation.__dict__)
print('\n-> Checksums are:',string,'type is:',type(string))
print('low density files are:', low_density_files)
print("End")
