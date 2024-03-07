import json 
import os
import yaml
import ipaddress
from ipaddress import IPv4Address, IPv4Network
from enum import Enum

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
  file_path= './assets/cyborg_complete_ip_map.json'
  
  with open(file_path, 'w') as file:
      json.dump(subnet_labels, file)
  return subnet_labels


#To map default Ip from Cyborg to actual ip  
def translate_intial_red_obs(data):
    with open('./assets/openstack_ip_map.json', 'r') as file:
      ip_mapping=json.load(file)
    # Replace IP addresses and subnet based on hostname
    print(ip_mapping)
    
    for key, value in ip_mapping.items():
        if value == 'User0':
            new_ip= key
        elif value == 'user_subnet':
            new_subnet= key
    print('new ip is:',new_ip,'subnet is:',new_subnet)
    print(data['User0']['Interface'][0])
    data['User0']['Interface'][0]['IP Address']= IPv4Address(new_ip)
    data['User0']['Interface'][0]['Subnet']= IPv4Network(new_subnet)
    print('\n Data is:',data)
    return data
    
    
class TrinaryEnum(Enum):
    TRUE = 1
    FALSE = 0
    UNKNOWN = 2

class utils:
  def __init___(self):
     TrinaryEnum= TrinaryEnum(Enum)
    

  def get_success_status(self,data):
    # Map string representations to TrinaryEnum values
    #print('data in get success is:',data)
    #print('\n \n **** data is:',data['success'])
    success_map = {
        True: True,
        False: False
    }
    # Use the map to return the corresponding TrinaryEnum value, defaulting to UNKNOWN
    return {'success': success_map.get(data['success'], TrinaryEnum.UNKNOWN)}


  def transform_DiscoverRemoteSystems(self,data):
    # Parsing and setting success on the input data
    transformed = self.get_success_status(data)

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

  # Convert the network services data to the required format
  def transform_DiscoverNetworkServices(self,data):
    formatted_data = {}
    for key, value in data.items():
        if key == "success":
            formatted_data[key] = self.get_success_status(data)
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




  # Convert the Exploit remote services data to the required format
  def transform_ExploitRemoteService(self,data):
    pass

 
  # Convert the Exploit remote services data to the required format
  def transform_PrivilegeEscalate(self,data):
    pass




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
     #print(f"The value of '{name}' is: {alt_name}")
     return alt_name
   
       
if __name__=='__main__':
   
  utils=utils()
  # Original data
  data = {
    "success":"False", 
    "10.0.10.0/24": {'10.0.10.12', '10.0.10.13', '10.0.10.14', '10.0.10.15', '10.0.10.16'}
         }
         
  data1 = {
    "success": "True", 
    "10.0.214.187": {'21', '22'}
   }
  # Convert the original data
  converted_data = utils.transform_DiscoverNetworkServices(data1)
  print(converted_data)
 # Convert the original data
  converted_data = utils.transform_ExploitRemoteService(data)
  print(converted_data)

  # Convert the original data
  converted_data = utils.transform_PrivilegeEscalate(data1)
  print(converted_data)





