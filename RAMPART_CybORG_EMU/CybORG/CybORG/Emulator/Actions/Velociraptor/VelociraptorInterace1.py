import json

import grpc
import time
import yaml
from pyvelociraptor import api_pb2_grpc, api_pb2


class VelociraptorInterface:

    def __init__(self, credentials_file):

        super().__init__()

        with open(credentials_file, "r") as input_fp:
            self.config = yaml.safe_load(input_fp)

        self.credentials = grpc.ssl_channel_credentials(
            root_certificates=self.config["ca_certificate"].encode("utf8"),
            private_key=self.config["client_private_key"].encode("utf8"),
            certificate_chain=self.config["client_cert"].encode("utf8")
        )

        # OPTIONS FOR CONNECTION TO VELOCIRAPTOR SERVER
        self.options = (('grpc.ssl_target_name_override', "VelociraptorServer",),)

        self.channel = None
        self.stub = None

    credentials_file_velociraptor_interface_dict = {}

    @classmethod
    def get_velociraptor_interface(cls, credentials_file):
        if credentials_file in cls.credentials_file_velociraptor_interface_dict:
            return cls.credentials_file_velociraptor_interface_dict[credentials_file]

        velociraptor_interface = VelociraptorInterface(credentials_file)
        cls.credentials_file_velociraptor_interface_dict[credentials_file] = velociraptor_interface
        return velociraptor_interface

    def __enter__(self):

        self.channel = grpc.secure_channel(self.config["api_connection_string"], self.credentials, self.options)
        return api_pb2_grpc.APIStub(self.channel)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.channel.close()
        self.channel = None
        return False

    def get_client_list(self):

        with self as stub:

            query = f"SELECT * FROM clients()"
            request = api_pb2.VQLCollectorArgs(Query=[api_pb2.VQLRequest(VQL=query)])

            client_list = []
            for response in stub.Query(request):
                if response.Response:
                    rows = json.loads(response.Response)

                    if len(rows) > 0:
                        client_list += rows

        return client_list

    def get_server_glob(self):

        with self as stub:

            query = f"SELECT * FROM glob(globs=\"/proc/*/fd/*\")"

            request = api_pb2.VQLCollectorArgs(Query=[api_pb2.VQLRequest(VQL=query)])

            glob_output = []
            for response in stub.Query(request):
                if response.Response:
                    rows = json.loads(response.Response)

                    if len(rows) > 0:
                        glob_output += rows

        return glob_output

    def get_client_id_from_hostname(self, hostname):

        client_id = None
        with self as stub:
            # GET CLIENT-ID OF HOST WITH HOSTNAME self.hostname
            query = f"SELECT client_id FROM clients() WHERE os_info.hostname = '{hostname}'"
            request = api_pb2.VQLCollectorArgs(Query=[api_pb2.VQLRequest(VQL=query)])

            for response in stub.Query(request):
                if response.Response:
                    rows = json.loads(response.Response)

                    if len(rows) > 0:
                        client_id = rows[0].get("client_id")
                        break

        return client_id

    @staticmethod
    def get_environment_string(environment_dict):
        environment_string = None
        if isinstance(environment_dict, dict):
            environment_string = "dict("
            is_not_first = False
            for key, value in environment_dict.items():
                if is_not_first:
                    environment_string += ","
                is_not_first = True
                environment_string += f"{key}='{value}'"
            environment_string += ")"

        return environment_string

    @staticmethod
    def cancel_flow(stub, client_id, flow_id):
        query = f"""
SELECT cancel_flow(client_id="{client_id}", flow_id="{flow_id}") FROM scope() 
"""
        request = api_pb2.VQLCollectorArgs(Query=[api_pb2.VQLRequest(VQL=query)])
        stub.Query(request)

        query = f"SELECT * FROM flows(client_id='{client_id}', flow_id='{flow_id}')"

        request = api_pb2.VQLCollectorArgs(Query=[api_pb2.VQLRequest(VQL=query)])

        flow_not_cancelled = True
        while flow_not_cancelled:

            for response in stub.Query(request):
                if response.Response:
                    rows = json.loads(response.Response)
                    if len(rows) > 0:
                        state = rows[0].get("state")
                        print("State from cancel flow is:",state)
                        if state == "ERROR":
                            flow_not_cancelled = False
                            break

            time.sleep(0.1)

    def execute_client_artifact(self, client_id, artifact_name, environment_dict=None, timeout=10, max_retries=3):

        with self as stub:

            flow_not_finished = True

            num_retries = 0
            while num_retries < max_retries and flow_not_finished:

                # SUBMIT EXECUTION OF THE Generic.System.Pstree ARTIFACT FOR CLIENT client_id
                # GET FLOW-ID OF THE EXECUTION FROM RESPONSE
                if environment_dict is None:
                    query = f"""
SELECT collect_client(
client_id='{client_id}', artifacts='{artifact_name}'
).flow_id AS FLOW_ID FROM scope()
"""
                else:
                    environment_string = self.get_environment_string(environment_dict)
                    query = f"""
SELECT collect_client(
client_id='{client_id}', artifacts='{artifact_name}', env={environment_string}
).flow_id AS FLOW_ID FROM scope()
"""

                request = api_pb2.VQLCollectorArgs(Query=[api_pb2.VQLRequest(VQL=query)])

                flow_id = None
                for response in stub.Query(request):
                    if response.Response:
                        rows = json.loads(response.Response)

                        if len(rows) > 0:
                            flow_id = rows[0].get("FLOW_ID")
                            break

                if flow_id is None:
                    return None

                # GET STATUS OF EXECUTION (FLOW) WITH FLOW-ID flow_id
                # WAIT UNTIL THE STATUS IS "FINISHED"
                query = f"SELECT * FROM flows(client_id='{client_id}', flow_id='{flow_id}')"

                request = api_pb2.VQLCollectorArgs(Query=[api_pb2.VQLRequest(VQL=query)])

                start_time = int(time.time())
                counter=0
                while flow_not_finished:
                    print('Start time:',start_time)
                    for response in stub.Query(request):
                        print('In stub.query request response')
                        if response.Response:
                            print('In response.response')
                            rows = json.loads(response.Response)
                            if len(rows) > 0:
                                state = rows[0].get("state")
                                counter+=1
                                print('state is:',state,'counter is',counter)
                                if state == "FINISHED":
                                    flow_not_finished = False
                                    break
                                else:
                                  print('in else')
                                  current_time = int(time.time())
                                  if current_time - start_time > timeout:
                                    print('Cancelling flow')
                                    self.cancel_flow(stub, client_id, flow_id)
                                    print('Cancelled!!')
                                    num_retries += 1
                                    break

                    time.sleep(0.1)
                    print('retry number: ',num_retries)
            if flow_not_finished:
                return None

            # GET OUTPUT FROM ARTIFACT
            query = f"""
SELECT * FROM flow_results(flow_id='{flow_id}', client_id='{client_id}', artifact='{artifact_name}')
"""

            request = api_pb2.VQLCollectorArgs(Query=[api_pb2.VQLRequest(VQL=query)])

            output_list = []
            for response in stub.Query(request):
                if response.Response:
                    output_list += json.loads(response.Response)

            return output_list
