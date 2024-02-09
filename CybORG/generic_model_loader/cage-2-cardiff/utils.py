import json 
import os
import yaml
import ipaddress
from ipaddress import IPv4Address, IPv4Network
from enum import Enum


class TrinaryEnum(Enum):
    TRUE = 1
    FALSE = 0
    UNKNOWN = 2

# Original data
data = {
    "success":"False", 
    "10.0.10.0/24": {'10.0.10.12', '10.0.10.13', '10.0.10.14', '10.0.10.15', '10.0.10.16'}
}


def get_success_status(data):
    # Map string representations to TrinaryEnum values
    success_map = {
        "True": TrinaryEnum.TRUE,
        "False": TrinaryEnum.FALSE
    }
    # Use the map to return the corresponding TrinaryEnum value, defaulting to UNKNOWN
    return {'success': success_map.get(data['success'], TrinaryEnum.UNKNOWN)}


def transform_DiscoverRemoteSystems(data):
    # Parsing and setting success on the input data
    transformed = get_success_status(data)

    for subnet, ips in data.items():
        if subnet != "success":
            network = IPv4Network(subnet)
            for ip in ips:
                transformed[str(ip)] = {
                    "Interface": [{
                        "IP Address": IPv4Address(ip),
                        "Subnet": network
                    }]
                }
    return transformed

print(transform_DiscoverRemoteSystems(data))



data1 = {
    "success": "True", 
    "10.0.214.187": {'21', '22'}
}


# Convert the network services data to the required format
def transform_DiscoverNetworkServices(data):
    formatted_data = {}
    for key, value in data.items():
        if key == "success":
            formatted_data[key] = get_success_status(data)
        else:
            # Convert set of ports into the required list of dictionaries
            processes = []
            for port in value:
                connection = {
                    'Connections': [{
                        'local_port': int(port),
                        'local_address': ipaddress.IPv4Address(key)
                    }]
                }
                processes.append(connection)
            interface = [{
                'IP Address': ipaddress.IPv4Address(key)
            }]
            formatted_data[key] = {
                'Processes': processes,
                'Interface': interface
            }
    return formatted_data

# Convert the original data
converted_data = transform_DiscoverNetworkServices(data1)
print(converted_data)


# Convert the Exploit remote services data to the required format
def transform_ExploitRemoteService(data):
    pass

# Convert the original data
converted_data = transform_ExploitRemoteService(data1)
print(converted_data)


# Convert the Exploit remote services data to the required format
def transform_PrivilegeEscalate(data):
    pass

# Convert the original data
converted_data = transform_PrivilegeEscalate(data1)
print(converted_data)




class name_conversion():
   def __init__(self,path):
     with open(path,'r') as f:
         self.data = yaml.safe_load(f)
     #print('Data is:',self.data)
     
   def fetch_alt_name(self,name):
     if name in self.data:
        alt_name = self.data[name]
     else:
        for key, value in self.data.items():
          if value == name:
            alt_name = key
     print(f"The value of '{name}' is: {alt_name}")
     return alt_name
   
       
if __name__=='__main__':
   c2o=name_conversion()
   c2o.fetch_alt_name() 


def parse_and_store_ips_host_map(blue_initial_obs):
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
  #print('Subnet labels are:',subnet_labels)
  if not os.path.exists('./assets'):
       os.makedirs('./assets')
  file_path= './assets/ip_map.json'
  
  with open(file_path, 'w') as file:
      json.dump(subnet_labels, file)
  return subnet_labels
