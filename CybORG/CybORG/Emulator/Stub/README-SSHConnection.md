To run the SSHConnectionServer, provide 4 arguments:


python SSHConnectionServer.py <connection_key> <hostname> <username> <path-to-rsa-key-file>


The <connection_key> uniquely identifies this particular SSHConnectionServer, and this same key is provided by an SSHConnectionClient when
sending command to be executed to the SSHConnectionServer.


Example:

python SSHConnectionServer.py A localhost ninehs /home/ninehs/.ssh/id_rsa



To run an SSHConnectionClient, provide the connection_key to the SSHConnectionServer.


python SSHConnectionClient.py <connection_key>


Feed a command that you can run on <hostname> to the standard input of the SSHConnectionClient:


echo "ls -l" | python SSHConnectionClient.py A

