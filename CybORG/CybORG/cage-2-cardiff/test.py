import inspect


"""
def wrap():
    print("In inspection")
    pass

lines = inspect.getsource(wrap)
print(lines)






import re

def is_word(s):
    return bool(re.match(r"^[A-Za-z]+", s))

print(is_word("User_subnet"))  # True
print(is_word("10.0.214.176/28"))  # True
print(is_word("10.0.214.176"))  # True



from ipaddress import IPv4Address

# Your IP map dictionary
from ipaddress import IPv4Address

# Initial IP map dictionary with IPv4Address objects
ip_map = {
    'Enterprise0': IPv4Address('10.0.11.24'),
    'Enterprise1': IPv4Address('10.0.11.20'),
    'Enterprise2': IPv4Address('10.0.11.28'),
    'Defender': IPv4Address('10.0.11.17'),
    'Op_Server0': IPv4Address('10.0.99.169'),
    'Op_Host0': IPv4Address('10.0.99.167'),
    'Op_Host1': IPv4Address('10.0.99.170'),
    'Op_Host2': IPv4Address('10.0.99.162'),
    'User0': IPv4Address('10.0.94.178'),
    'User1': IPv4Address('10.0.94.180'),
    'User2': IPv4Address('10.0.94.190'),
    'User3': IPv4Address('10.0.94.187'),
    'User4': IPv4Address('10.0.94.181')
}

# Convert each IPv4Address object to its string representation
ip_map = {key: str(value) for key, value in ip_map.items()}

# Print the updated dictionary
print(ip_map)



blue_initial_obs = {
    'Defender': ['10.0.120.144/28', '10.0.120.156', 'Defender', 'None', 'No'],
    'Enterprise0': ['10.0.120.144/28', '10.0.120.152', 'Enterprise0', 'None', 'No'],
    'Enterprise1': ['10.0.120.144/28', '10.0.120.158', 'Enterprise1', 'None', 'No'],
    'Enterprise2': ['10.0.120.144/28', '10.0.120.155', 'Enterprise2', 'None', 'No'],
    'Op_Host0': ['10.0.110.32/28', '10.0.110.38', 'Op_Host0', 'None', 'No'],
    'Op_Host1': ['10.0.110.32/28', '10.0.110.42', 'Op_Host1', 'None', 'No'],
    'Op_Host2': ['10.0.110.32/28', '10.0.110.46', 'Op_Host2', 'None', 'No'],
    'Op_Server0': ['10.0.110.32/28', '10.0.110.34', 'Op_Server0', 'None', 'No'],
    'User0': ['10.0.214.176/28', '10.0.214.186', 'User0', 'None', 'No'],
    'User1': ['10.0.214.176/28', '10.0.214.187', 'User1', 'None', 'No'],
    'User2': ['10.0.214.176/28', '10.0.214.182', 'User2', 'None', 'No'],
    'User3': ['10.0.214.176/28', '10.0.214.180', 'User3', 'None', 'No'],
    'User4': ['10.0.214.176/28', '10.0.214.189', 'User4', 'None', 'No']
}

# Create a dictionary to map subnets to hosts
subnet_to_hosts = {}

for host, details in blue_initial_obs.items():
    subnet = details[0]  # The subnet is the first item in the details list
    if subnet not in subnet_to_hosts:
        subnet_to_hosts[subnet] = [host]
    else:
        subnet_to_hosts[subnet].append(host)

# Print the subnets and their corresponding hosts
for subnet, hosts in subnet_to_hosts.items():
    print(f"Subnet: {subnet} has hosts: {', '.join(hosts)}")




blue_initial_obs = {
    'Defender': ['10.0.120.144/28', '10.0.120.156', 'Defender', 'None', 'No'],
    'Enterprise0': ['10.0.120.144/28', '10.0.120.152', 'Enterprise0', 'None', 'No'],
    'Enterprise1': ['10.0.120.144/28', '10.0.120.158', 'Enterprise1', 'None', 'No'],
    'Enterprise2': ['10.0.120.144/28', '10.0.120.155', 'Enterprise2', 'None', 'No'],
    'Op_Host0': ['10.0.110.32/28', '10.0.110.38', 'Op_Host0', 'None', 'No'],
    'Op_Host1': ['10.0.110.32/28', '10.0.110.42', 'Op_Host1', 'None', 'No'],
    'Op_Host2': ['10.0.110.32/28', '10.0.110.46', 'Op_Host2', 'None', 'No'],
    'Op_Server0': ['10.0.110.32/28', '10.0.110.34', 'Op_Server0', 'None', 'No'],
    'User0': ['10.0.214.176/28', '10.0.214.186', 'User0', 'None', 'No'],
    'User1': ['10.0.214.176/28', '10.0.214.187', 'User1', 'None', 'No'],
    'User2': ['10.0.214.176/28', '10.0.214.182', 'User2', 'None', 'No'],
    'User3': ['10.0.214.176/28', '10.0.214.180', 'User3', 'None', 'No'],
    'User4': ['10.0.214.176/28', '10.0.214.189', 'User4', 'None', 'No']
}

# Initialize a dictionary to hold subnet labels
subnet_labels = {}

for host, details in blue_initial_obs.items():
    subnet = details[0]
    if "Enterprise" in host:
        subnet_labels[subnet] = "enterprise_subnet"
    elif "Op_Host" in host or "Op_Server" in host:
        subnet_labels[subnet] = "operation_subnet"
    elif "User" in host:
        subnet_labels[subnet] = "user_subnet"
    subnet_labels[details[1]]=host
print('Subnet labels are:',subnet_labels)
    # Add more conditions here if there are other types



import json
from ipaddress import IPv4Address, IPv4Network

# Updated first dictionary with the correct enums replaced by their names as strings
data = {
    'success': 'UNKNOWN',
    'User0': {
        'Interface': [{
            'Interface Name': 'eth0',
            'IP Address': IPv4Address('10.0.214.186'),
            'Subnet': IPv4Network('10.0.214.176/28')
        }],
        'Sessions': [{
            'Username': 'SYSTEM',
            'ID': 0,
            'Timeout': 0,
            'PID': 2384,
            'Type': 'RED_ABSTRACT_SESSION',
            'Agent': 'Red'
        }],
        'Processes': [{'PID': 2384, 'Username': 'SYSTEM'}],
        'System info': {
            'Hostname': 'User0',
            'OSType': 'WINDOWS',
            'OSDistribution': 'WINDOWS_SVR_2008',
            'OSVersion': 'W6_1_7601',
            'Architecture': 'x64'
        }
    }
}

# Second dictionary for IP mapping
ip_mapping = {
    "10.0.20.200": "Defender",
    "10.10.20.0/24": "enterprise_subnet",
    "10.10.20.10": "Enterprise0",
    "10.10.20.11": "Enterprise1",
    "10.10.20.12": "Enterprise2",
    "10.10.30.0/24": "operation_subnet",
    "10.10.10.17": "Op_Host0",
    "10.10.10.18": "Op_Host1",
    "10.10.10.19": "Op_Host2",
    "10.10.10.20": "Op_Server0",
    "10.10.10.0/24": "user_subnet",
    "10.10.10.12": "User0",
    "10.10.10.13": "User1",
    "10.10.10.14": "User2",
    "10.10.10.15": "User3",
    "10.10.10.16": "User4"
}

# Replace IP addresses and subnet based on hostname

for key, value in ip_mapping.items():
        if value == 'User0':
            new_ip= key
        elif value == 'user_subnet':
            new_subnet= key
print('new ip is:',new_ip,'subnet is:',new_subnet)
print(data['User0']['Interface'][0])
data['User0']['Interface'][0]['Ip Address']= IPv4Address(new_ip)
data['User0']['Interface'][0]['Subnet']= IPv4Network(new_subnet)
      

# Print the updated dictionary
print(data )
"""


host= {'Processes': [{'PID': 12122, 'PPID': 1, 'Service Name': 'femitter', 'Username': 'SYSTEM'}]}
host_baseline={'Processes:': [{'pid': 4}, {'pid': 832}, {'pid': 4400}]}
if 'Processes' in host:
                baseline_processes = host_baseline.get('Processes', [])
                print('\n-> Baseline processes:',baseline_processes)



