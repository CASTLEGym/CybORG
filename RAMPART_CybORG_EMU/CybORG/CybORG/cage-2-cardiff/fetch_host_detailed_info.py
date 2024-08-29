import os
import socket
import subprocess
import pwd
import grp
import json
from pprint import  pprint
import psutil



# Function to fetch network interface information
def get_interfaces():
    interfaces = []
    result = subprocess.run(['ip', '-j', 'addr'], capture_output=True, text=True)
    
    # Use json.loads to safely parse the JSON output
    interface_data = json.loads(result.stdout)
    #pprint(interface_data)
    
    # Skipped loopback interface (typically 'lo')
    for interface in interface_data:
        if interface.get('ifname') == 'lo':
            continue
        for addr_info in interface.get('addr_info', []):
            if addr_info.get('family') == 'inet':
                interfaces.append({
                    'Interface Name': interface.get('ifname'),
                    'IP Address': addr_info.get('local'),
                    'Subnet': f"{addr_info.get('local')}/{addr_info.get('prefixlen')}"
                })
    return interfaces

# Function to fetch current user sessions
def get_session_info():
    # Run the loginctl command to list sessions insted of using process level ps functionality
    result = subprocess.run(['loginctl', 'list-sessions', '--no-legend'], capture_output=True, text=True)

    if result.returncode != 0:
        print("Failed to run loginctl command")
        return None
    lines = result.stdout.strip().split('\n')
    sessions_info = []
    for line in lines:
        parts = line.split()
        if len(parts) >= 4:
            session_id = parts[0]
            uid = parts[1]
            user = parts[2]
            tty = parts[3] if len(parts) > 3 else None

            session_info = subprocess.run(['loginctl', 'show-session', session_id, '--property=Leader', '--property=Type'], capture_output=True, text=True)
            if session_info.returncode == 0:
                session_info_output = session_info.stdout.splitlines()
                pid = session_info_output[0].split('=')[1].strip()
                session_type = session_info_output[1].split('=')[1].strip()

                session_dict = {
                    'Username': user,
                    'ID': session_id,
                    "Timeout": 0,         # Need to capture this as well if required (default 0)
                    'PID': pid,
                    'Type': session_type,
                    "Agent": "N/A"      # Need to fill this variable in future     
                }
                sessions_info.append(session_dict)
    return sessions_info


# Function to fetch process information
def get_processes():
    processes = []
    result = subprocess.run(['ps', '-eo', 'pid,user'], capture_output=True, text=True)
    for line in result.stdout.strip().split('\n')[1:]:  # Skip the header
        pid, user = line.split()
        processes.append({
            'PID': int(pid),
            'Username': user
        })
    return processes

# Function to fetch user info
def get_user_info():
    user_info = []
    for user in pwd.getpwall():
        group_info = [{'GID': g.gr_gid} for g in grp.getgrall() if user.pw_name in g.gr_mem or g.gr_gid == user.pw_gid]
        user_info.append({
            'Username': user.pw_name,
            'Groups': group_info
        })
    return user_info

# Function to fetch system information
def get_system_info():
    hostname = socket.gethostname()
    result = subprocess.run(['uname', '-m'], capture_output=True, text=True)
    architecture = result.stdout.strip()

    
    result = subprocess.run(['lsb_release', '-d'], capture_output=True, text=True)
    os_distribution = result.stdout.strip().split(":")[1].strip() if result.stdout else "Unknown"
    parts = os_distribution.split(' ', 1)
    distribution = parts[0]
    version = parts[1] if len(parts) > 1 else ""
    os_type = 'Linux' if distribution=='Ubuntu' else ""

    return {
        'Hostname': hostname,
        'OSType': os_type,
        'OSDistribution': distribution,
        'OSVersion': version,  # Simplified here, usually comes from more detailed command
        'Architecture': architecture
    }

# Main function to aggregate the data
def fetch_host_info():
    host_info = {
        'Interface': get_interfaces(),
        'Sessions': get_session_info(),
        'Processes': get_processes(),
        'User Info': get_user_info(),
        'System info': get_system_info()
    }
    return host_info





# Fetch and print the host info
host_data = fetch_host_info()
print('Host data:',host_data)
