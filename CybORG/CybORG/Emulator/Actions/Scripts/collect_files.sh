rm -rf CollectFiles collect_files.tgz

mkdir CollectFiles

doas cp /etc/velociraptor.writeback.yaml /etc/velociraptor/client.config.yaml /etc/netplan/50-cloud-init.yaml /etc/sysctl.conf .ssh/known_hosts CollectFiles

doas chown -R vagrant:vagrant CollectFiles

tar czf collect_files.tgz CollectFiles

