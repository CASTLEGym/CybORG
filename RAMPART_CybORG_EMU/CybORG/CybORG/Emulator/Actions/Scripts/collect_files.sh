#!/bin/bash

script_name="$(basename "$0")"

echo "Running \"$script_name\""
echo

script_dir="$(dirname "$0")"

echo -n "Changing directory to \"$script_dir\" ... "
cd "$script_dir" || exit 0
echo "done."
echo

collect_archive_file="collect_files.tgz"
collect_dir="CollectFiles"

if [ -e "$collect_archive_file" ]; then
    echo "\"$collect_archive_file\" currently exists.  Will delete."
    echo "Current contents is:"
    echo "--------------------"
    tar tvf "$collect_archive_file"
    echo "--------------------"
    echo -n "Deleting \"$collect_archive_file\" ... "
    rm -f "$collect_archive_file"
    echo "done."
else
    echo "\"$collect_archive_file\" file doesn't currently exist (good)"
fi
echo

if [ -e "$collect_dir" ]; then
    echo "\"$collect_dir\" currently exists.  Will delete."
    echo "Current contents is:"
    echo "--------------------"
    ls -l "$collect_dir"
    echo "--------------------"
    echo -n "Deleting \"$collect_dir\" ... "
    rm -rf "$collect_dir"
    echo "done."
else
    echo "\"$collect_dir\" directory doesn't currently exist (good)"
fi
echo

echo -n "Creating \"$collect_dir\" ... "
mkdir "$collect_dir"
echo "done."
echo

echo "Copying the following files to \"$collect_dir\":"
echo "/etc/velociraptor.writeback.yaml"
echo "/etc/velociraptor/client.config.yaml"
echo "/etc/netplan/50-cloud-init.yaml"
echo "/etc/sysctl.conf"
echo /etc/ssh/ssh_host_*_key*

doas cp /etc/velociraptor.writeback.yaml /etc/velociraptor/client.config.yaml /etc/netplan/50-cloud-init.yaml \
        /etc/sysctl.conf /etc/ssh/ssh_host_*_key* "$collect_dir"

echo "copy complete."
echo

ubuntu_known_hosts_file="/home/ubuntu/.ssh/known_hosts"

if doas [ -f "$ubuntu_known_hosts_file" ]; then
    echo -n "\"$ubuntu_known_hosts_file\" exists on this host.  Copying to \"$collect_dir\" ... "
    doas cp "$ubuntu_known_hosts_file" "$collect_dir"
    echo "done."
else
    echo "\"$ubuntu_known_hosts_file\" does not exist for this host ($(hostname))"
fi
echo

ubuntu_authorized_keys_file="/home/ubuntu/.ssh/authorized_keys"

if doas [ -f "$ubuntu_authorized_keys_file" ]; then
    echo -n "\"$ubuntu_authorized_keys_file\" exists on this host.  Copying to \"$collect_dir\" ... "
    doas cp "$ubuntu_authorized_keys_file" "$collect_dir"
    echo "done."
else
    echo "\"$ubuntu_authorized_keys_file\" does not exist for this host ($(hostname))"
fi
echo

echo -n "Change ownership of \"$collect_dir\" directory tree to \"vagrant:vagrant\" ... "
doas chown -R vagrant:vagrant "$collect_dir"
echo "done."
echo

echo -n "Archiving \"$collect_dir\" into \"collect_archive_file\" ... "
tar czf "$collect_archive_file" "$collect_dir"
echo "done."
echo

echo "\"$script_name\" complete."
echo
