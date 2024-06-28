from .RunProcessAction import RunProcessAction


class SSHConnectionClientAction(RunProcessAction):

    def __init__(self, credentials_file, hostname, connection_key, command):

        super().__init__(
            credentials_file=credentials_file,
            hostname=hostname,
            command=f"echo '{command}' | python /usr/local/scripts/SSHConnectionClient.py {connection_key}"
        )
