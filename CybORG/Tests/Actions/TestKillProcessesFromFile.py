from CybORG.Emulator.Actions.Velociraptor import KillProcessesFromFileAction
from CybORG.Emulator.Actions.Velociraptor.RunProcessAction import RunProcessAction

credentials_file = "prog_client.yaml"

create_foobar_action = RunProcessAction(
    credentials_file=credentials_file,
    hostname="TESTDOCKER1", command="""
cat > FOOBAR1.sh <<END
while true; do
    sleep 10
done > /dev/null 2>&1
END

ln FOOBAR1.sh FOOBAR2.sh

cat > killProcessListing.txt <<END
FOOBAR1.sh
FOOBAR2.sh
END

bash FOOBAR1.sh > /dev/null 2>&1 &
bash FOOBAR2.sh > /dev/null 2>&1 &
"""
)

create_foobar_observation = create_foobar_action.execute(None)

kill_processes_from_file_action = KillProcessesFromFileAction(
    credentials_file=credentials_file, hostname="TESTDOCKER1", file_path="killProcessListing.txt"
)

kill_processes_from_file_observation = kill_processes_from_file_action.execute(None)

print("foo")
