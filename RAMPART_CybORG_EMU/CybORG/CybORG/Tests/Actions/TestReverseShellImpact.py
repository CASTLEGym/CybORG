import sys
import argparse

from CybORG.Emulator.Actions.Velociraptor.ReverseShellImpactAction import ReverseShellImpactAction

parser = argparse.ArgumentParser(
    prog="TestReverseShellImpact.py",
    description="Test the ReverseShellImpactAction"
)

parser.add_argument(
    "-n", "--connection-key", required=True,
    help="key used to unique identify reverse shell connection"
)

parser.add_argument(
    "-p", "--server-port", required=True,
    help="port on which reverse-shell-server is listening for reverse-shell-client connections"
)

parser.add_argument(
    "-c", "--command", required=True,
    help="command to submit to the compromised machine"
)

args = parser.parse_args()

credentials_file = "prog_client3.yaml"

haraka_exploit_action = ReverseShellImpactAction(
    credentials_file=credentials_file,
    hostname="TESTDOCKER1",
    connection_key=args.connection_key,
    reverse_shell_server_port=args.server_port,
    reverse_shell_command=args.command
)

haraka_exploit_observation = haraka_exploit_action.execute(None)
print(haraka_exploit_observation.Stdout)
