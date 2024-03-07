from CybORG.Shared import Observation


class SshObservation(Observation):

    def __init__(self, success, token=None, local_socket_info=None, remote_socket_info=None, pid=None):
        super().__init__(success=success)

        self.token = token
        self.available_exploit = 'FTPDirTraversal'
        self.local_socket_info = local_socket_info
        self.remote_socket_info = remote_socket_info
        self.pid = pid

