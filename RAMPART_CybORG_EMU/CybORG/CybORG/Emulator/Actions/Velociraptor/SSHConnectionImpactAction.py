from .RunProcessAction import RunProcessAction


class SSHConnectionImpactAction(RunProcessAction):

    def __init__(self, credentials_file, hostname, connection_key, command):

        super().__init__(
            credentials_file=credentials_file,
            hostname=hostname,
            command=f"echo '{command}' | " +
                    f"python /usr/local/scripts/python/SSHConnectionTerminalClient.py {connection_key}"
        )
