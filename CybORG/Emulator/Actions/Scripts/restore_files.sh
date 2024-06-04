mkdir CollectFiles

tar xf collect_files.tgz

doas cp CollectFiles/velociraptor.writeback.yaml /etc/velociraptor.writeback.yaml
doas bash -c "cp CollectFiles/client.config.yaml /etc/velociraptor/client.config.yaml; chown velociraptor:velociraptor /etc/velociraptor/client.config.yaml"
doas cp CollectFiles/50-cloud-init.yaml /etc/netplan/50-cloud-init.yaml
doas cp CollectFiles/sysctl.conf /etc/sysctl.conf

doas sysctl --system
doas netplan apply

doas systemctl enable velociraptor_client
doas systemctl start velociraptor_client