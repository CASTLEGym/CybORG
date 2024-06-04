from CybORG.Emulator.Actions.Velociraptor.RunProcessAction import RunProcessAction


class KillProcessAction(RunProcessAction):

    def __init__(self, credentials_file, hostname, pid):

        super().__init__(
            credentials_file=credentials_file,
            hostname=hostname,
            command=f"kill {pid}"
        )
