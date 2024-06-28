# Using SshConnectionServer.py Script

The SshConnectionServer.py script runs a server that

* Establishes an ssh connection to a pre-specified remote host
* Persists the ssh connection as long as the server is running
* Executes a shell on the remote host with which it communicates over the ssh connection
* Opens a separate UNIX socket over which it can receive commands to relay to the remote shell and relay back the
  output from these commands.

The SSHConnectionServer.py script is run as follows:
```
python SSHConnection.py [-h] -n CONNECTION_KEY -m HOSTNAME -u USERNAME (-k PRIVATE_KEY_FILE | -p PASSWORD)
                        [-d] [-c CLIENT_PORT] [-s SERVER_PORT]
```

The options are as follows:

| Option              | Description                                                                                                                                                                            |
|---------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| -h                  | Print help message                                                                                                                                                                     |
| -n CONNECTION_KEY   | (REQUIRED) A unique key that another program can use to communicate with the SSHConnectionServer.py in order to submit commands to the shell and receive the output of these commands. |
| -m HOSTNAME         | (REQUIRED) The hostname or ip-address of the machine with which the SSHConnectionServer.py make an ssh connection.                                                                     |
| -u USERNAME         | (REQUIRED) The name if the user account the SSHConnectionServer.py script uses to login to the HOSTNAME machine.                                                                       |
| -k PRIVATE_KEY_FILE | (You must use either this option or the -p option, but not both) The path to the private key file for the USERNAME user to login to the HOSTNAME machine using dual-key encrytion.     |
| -p PASSWORD         | (You must use either this option or the -k option, but not both) The password for the USERNAME user to login to the HOSTNAME machine.                                                  |
| -d                  | Use this option if you want to run the SSHConnectionServer.py script as a daemon.                                                                                                      |
| -c CLIENT_PORT      | Use this option if you want the SSHConnectionServer.py script to connect to the ssh-server on HOSTNAME using a specified local port CLIENT_PORT.                                       |
| -s SERVER_PORT      | Use this option if you want the SSHConnectionServer.py script if the ssh-server on HOSTNAME is listening on port SERVER_PORT rather then the standard ssh-server port (22).            |

python SSHConnectionServer.py <connection_key> &lt;hostname> &lt;username> <path-to-rsa-key-file>


## Example:

python SSHConnectionServer.py -n ABC -m localhost -u user1 -k /home/user1/.ssh/id_rsa

This connects to the `localhost` machine, logging in as `user1` using the `/home/user1/.ssh/id_rsa` private key file.


# Using the SSHConnectionClient.py script

To submit shell commands to the running SSHConnectionServer.py script that has CONNECTION_KEY=ABC, the
SSHConnectionClient.py script is provided.  The usage is as follows:

```commandline
python SSHConnectionClient.py <CONNECTION_KEY>
```

where CONNECTION_KEY is the unique key that was specified when running the SSHConnectionServer.py script.

The SSHConnectionClient.py script accepts valid bash command-line input on its standard input, and the output of this
command-line is place on its standard output.

## Example

To execute the `ls -l` command to an SSHConnectionServer.py script that was run with unique key `ABC`,
you can enter the following command:

```
echo "ls -l" | python SSHConnectionClient.py ABC
```

The output of the command can be received on the standard output of the SSHConnectionClient.py script.
