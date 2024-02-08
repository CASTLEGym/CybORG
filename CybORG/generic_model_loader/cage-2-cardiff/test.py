import inspect

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


