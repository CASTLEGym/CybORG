# Provided dictionary
"""
ip_to_name = {
    "10.0.120.156": "Defender",
    "10.0.120.144/28": "enterprise_subnet",
    "10.0.120.152": "Enterprise0",
    "10.0.120.158": "Enterprise1",
    "10.0.120.155": "Enterprise2",
    "10.0.110.32/28": "operation_subnet",
    "10.0.110.38": "Op_Host0",
    "10.0.110.42": "Op_Host1",
    "10.0.110.46": "Op_Host2",
    "10.0.110.34": "Op_Server0",
    "10.0.214.176/28": "user_subnet",
    "10.0.214.186": "User0",
    "10.0.214.187": "User1",
    "10.0.214.182": "User2",
    "10.0.214.180": "User3",
    "10.0.214.189": "User4"
}

def get_subnet_ip(self,hostname,ip_to_name):
    # Reverse the dictionary to map names to IPs
    name_to_ip = {v: k for k, v in ip_to_name.items()}
    print(name_to_ip)
    # Subnet mappings
    subnet_mappings = {}
    # Loop through the input dictionary and extract subnet information
    for key, value in name_to_ip.items():
      if 'subnet' in key:
         subnet_mappings[key] = value

    print(subnet_mappings)


    if hostname in name_to_ip:
        ip = name_to_ip[hostname]
        print('ip is:',ip)
        # Determine which subnet the IP belongs to
        for subnet_name, subnet_ip in subnet_mappings.items():
            # Split the string by dots
            parts = subnet_ip.split('.')
            # Combine the first three parts with dots
            first_part = '.'.join(parts[:3])
            if subnet_ip in ip_to_name and ip.startswith(first_part):
                print('subnet Ip:',subnet_ip)
                return subnet_ip

    return None

# Example usages
print(get_subnet_ip("Op_Host0"))  # Should return "operation_subnet"
print(get_subnet_ip("Enterprise2"))  # Should return "enterprise_subnet"
print(get_subnet_ip("User2"))  # Should return "user_subnet"
"""

network_state = {}


def update_reward_information_dict(info_dict, server_name, username):
    if server_name not in info_dict:
        info_dict[server_name] = {'Sessions': []}
    info_dict[server_name]['Sessions'].append({'Username': username})


def delete_reward_information_dict(info_dict, server_name, username):
    if server_name in info_dict:
        sessions = info_dict[server_name]['Sessions']
        info_dict[server_name]['Sessions'] = [session for session in sessions if session['Username'] != username]

        # If there are no more sessions, remove the server entry
        if not info_dict[server_name]['Sessions']:
            del info_dict[server_name]

    return info_dict


update_reward_information_dict(network_state, 'User0', 'root')
print(network_state)
update_reward_information_dict(network_state, 'User0', 'ubuntu')
print(network_state)
update_reward_information_dict(network_state, 'User1', 'ubuntu')
print(network_state)

delete_reward_information_dict(network_state, 'User0', 'root')
print(network_state)
