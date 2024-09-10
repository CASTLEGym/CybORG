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

if [ -d "$collect_dir" ]; then
    echo "\"$collect_dir\" exists (it shouldn't)"
    echo "Removing \"$collect_dir\" ... "
    rm -rf "$collect_dir"
    echo "done."
else
    echo "\"$collect_dir\" does not exist (good)"
fi
echo

if [ -e "$collect_archive_file" ]; then
    echo "\"$collect_archive_file\" exists (important)"
    echo "untarring \"$collect_archive_file\" ... "
    tar xvf "$collect_archive_file"
    echo "done untarring \"$collect_archive_file\"."
else
    echo "\"$collect_archive_file\" DOES NOT EXIST!!!!  ERRORING OUT!!!!!!"
    exit 1
fi

echo -n "Changing into \"$collect_dir\" ... "
cd "$collect_dir" || exit 1
echo "done."

exec_command() {
    echo "Executing: \"$1\":"
    eval "$1"
    exit_status=$?
    echo

    if [ $exit_status -ne 0 ]; then
        echo "Error encountered executing:"
        echo "$@"
    fi
}

exec_command "doas cp ssh_host_*_key* /etc/ssh"
exec_command "doas systemctl restart ssh.service"
exec_command "doas cp velociraptor.writeback.yaml /etc/velociraptor.writeback.yaml"
exec_command "doas cp client.config.yaml /etc/velociraptor/client.config.yaml"
exec_command "doas chown velociraptor:velociraptor /etc/velociraptor/client.config.yaml"
exec_command "doas cp 50-cloud-init.yaml /etc/netplan/50-cloud-init.yaml"
exec_command "doas chmod 600 /etc/netplan/50-cloud-init.yaml"
exec_command "doas cp sysctl.conf /etc/sysctl.conf"
exec_command "doas sysctl --system"
exec_command "doas netplan apply"
exec_command "doas systemctl enable velociraptor_client"
exec_command "doas systemctl start velociraptor_client"
exec_command "doas bash -c 'echo -e \"ubuntu\nubuntu\" | passwd \"ubuntu\" > /dev/null 2>&1'"
exec_command "doas mkdir -p /usr/local/run"
exec_command "doas chmod a+rwxt /usr/local/run"

ubuntu_ssh_directory="/home/ubuntu/.ssh"

if ! doas [ -d "$ubuntu_ssh_directory" ]; then
    exec_command "doas mkdir \"$ubuntu_ssh_directory\""
else
    echo "\"$ubuntu_ssh_directory\" already exists.  Skipping creation."
    echo
fi

known_hosts_file="known_hosts"

ubuntu_known_hosts_file="/home/ubuntu/.ssh/$known_hosts_file"
if [ -f "$known_hosts_file" ]; then
    exec_command "doas cp \"$known_hosts_file\" \"$ubuntu_known_hosts_file\""
else
    echo "\"$known_hosts_file\" not in tar archive.  Skipping copy."
    echo
fi

authorized_keys_file="authorized_keys"

ubuntu_authorized_keys_file="/home/ubuntu/.ssh/$authorized_keys_file"
if [ -f "$authorized_keys_file" ]; then
    exec_command "doas cp \"$authorized_keys_file\" \"$ubuntu_authorized_keys_file\""
else
    echo "\"$authorized_keys_file\" not in tar archive.  Skipping copy."
    echo
fi

exec_command "doas chown -R ubuntu:ubuntu \"$ubuntu_ssh_directory\""

cd ..
echo "Changed to parent directory ($PWD)"

exec_command "rm -rf \"$collect_dir\" \"$collect_archive_file\""
