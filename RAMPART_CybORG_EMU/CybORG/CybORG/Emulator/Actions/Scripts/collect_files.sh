rm -rf CollectFiles collect_files.tgz

mkdir CollectFiles

doas cp /etc/velociraptor.writeback.yaml /etc/velociraptor/client.config.yaml /etc/netplan/50-cloud-init.yaml \
        /etc/sysctl.conf /etc/ssh/ssh_host_*_key* CollectFiles
        
ubuntu_known_hosts_file="/home/ubuntu/.ssh/known_hosts"

if doas [ -f "$ubuntu_known_hosts_file" ]; then
    doas cp "$ubuntu_known_hosts_file" CollectFiles
fi

ubuntu_authorized_keys_file="/home/ubuntu/.ssh/authorized_keys"

if doas [ -f "$ubuntu_authorized_keys_file" ]; then
    doas cp "$ubuntu_authorized_keys_file" CollectFiles
fi

doas chown -R vagrant:vagrant CollectFiles

tar czf collect_files.tgz CollectFiles
