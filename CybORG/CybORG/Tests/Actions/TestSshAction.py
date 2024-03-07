from CybORG.Emulator.Actions.SshAction import SshAction


sshAction = SshAction("172.17.0.2", "velociraptor", "velociraptor")
#sshAction = SshAction("172.17.0.3", "sftp_user", "art54")

sshAction.execute(None)

print("foo")