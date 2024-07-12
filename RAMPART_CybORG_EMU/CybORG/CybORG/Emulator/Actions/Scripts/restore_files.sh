rm -rf CollectFiles

tar xf collect_files.tgz

cd CollectFiles || exit 1
doas cp velociraptor.writeback.yaml /etc/velociraptor.writeback.yaml

doas cp client.config.yaml /etc/velociraptor/client.config.yaml
doas chown velociraptor:velociraptor /etc/velociraptor/client.config.yaml

doas cp 50-cloud-init.yaml /etc/netplan/50-cloud-init.yaml
doas chmod 600 /etc/netplan/50-cloud-init.yaml

doas cp sysctl.conf /etc/sysctl.conf

ubuntu_ssh_directory="/home/ubuntu/.ssh"

if ! doas [ -d "$ubuntu_ssh_directory" ]; then
    doas mkdir "$ubuntu_ssh_directory"
fi

known_hosts_file="known_hosts"

ubuntu_known_hosts_file="/home/ubuntu/.ssh/$known_hosts_file"
if [ -f "$known_hosts_file" ]; then
    doas cp "$known_hosts_file" "$ubuntu_known_hosts_file"
fi

authorized_keys_file="authorized_keys"

ubuntu_authorized_keys_file="/home/ubuntu/.ssh/$authorized_keys_file"
if [ -f "$authorized_keys_file" ]; then
    doas cp "$authorized_keys_file" "$ubuntu_authorized_keys_file"
fi

doas chown -R ubuntu:ubuntu "$ubuntu_ssh_directory"

doas sysctl --system
doas netplan apply

doas systemctl enable velociraptor_client
doas systemctl start velociraptor_client

doas bash -c 'echo -e "ubuntu\nubuntu" | passwd "ubuntu" > /dev/null 2>&1'

cd ..
rm -rf CollectFiles collect_files.tgz

doas mkdir -p /usr/local/run 
doas chmod a+rwxt /usr/local/run
