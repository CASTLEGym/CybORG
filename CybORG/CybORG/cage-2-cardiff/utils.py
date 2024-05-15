import json 
import os
import yaml
import ipaddress
from ipaddress import IPv4Address, IPv4Network
from enum import Enum, auto
import random

import re


with open('./assets/openstack_ip_map.json', 'r') as file:
      ip_mapping=json.load(file)

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



def translate_initial_blue_info(data):  
    info_dict=ip_mapping    
    update_dict=data
    for key in update_dict:
        if key in info_dict:
            ip_subnet = update_dict[key][0]
            ip_address = update_dict[key][1]

            # Update subnet if it's a network segment
            if '/' in ip_subnet:
                subnet_key = key + '_subnet'
                if subnet_key in info_dict:
                    update_dict[key][0] = info_dict[subnet_key]

            # Update IP address
            update_dict[key][1] = info_dict[key]

    return update_dict
  


#To map default Ip from Cyborg to actual ip  
def translate_intial_red_obs(data):
    
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
    

def modify_blue_by_red(blue_outcome,red_outcome,red_action,red_action_param):
    if red_action=='DiscoverRemoteSystems':
      return blue_outcome
    elif red_action=='DiscoverNetworkServices':
      print('red_outcome is:',red_outcome, 'red_action_param is:',red_action_param) 
      info={
        red_action_param:parse_DNS_data(red_outcome)
      }
      print('\n blue outcome is:',blue_outcome)
      blue_outcome.update(info)
      print('\n **Blue Info is:',blue_outcome)
      return blue_outcome


def parse_DNS_data(input_data):
    result = {}
    for key, value in input_data.items():
        if key != 'success':
            result[key] = {
                'Processes': [],
                'Interface': [{'IP Address': IPv4Address(key)}]
            }
            for process in value['Processes']:
                for connection in process['Connections']:
                    result[key]['Processes'].append({
                        'Connections': [{
                            'local_port': connection['local_port'],
                            'remote_port': random.randint(40000, 50000),
                            'local_address': connection['local_address']
                        }]
                    })
    return result[key]


def merge_dictionaries(dict1, dict2):
    merged_dict = {}
    for key in set(dict1.keys()).union(dict2.keys()):
      if key != 'success':  
        merged_dict[key] = []
        if key in dict1:
            merged_dict[key].append(dict1[key])
        if key in dict2:
            merged_dict[key].append(dict2[key])
    return merged_dict

    
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
    
    #commenting out since emulation provides this object
    success_map = {
        True: True,
        False: False
    }
    # Use the map to return the corresponding TrinaryEnum value, defaulting to UNKNOWN
    return {'success': success_map.get(data['success'], TrinaryEnum.UNKNOWN)}
    """
    return data['success']
    """



  def transform_decoy(self, data):
    # TO do : Remove PID and PPID as fixed to fetch from process and update 
    #       : If possible remove the propertiesa and set it during the decoy set up to lure/honeytrap. 
    #       : Remove the faked decoys that is not part of linux type decoys. 
    print('Data is:',data)
    formatted_data= self.get_success_status(data)
    host=data['host']
    username=data['username']
    decoyname=data['decoyname']

    decoyname= decoyname.lower()
    formatted_data[host] = {
            'Processes': [
                {
                    'PID': random.randint(1000,5000),  # Static PID since it's not provided in the input
                    'PPID': 1,                # Static PPID since it's not provided in the input
                    'Service Name': decoyname,  # Assuming a static service name; replace if variable
                    'Username': username
                }
            ]
        }
    
    #Decoy specific modification
    if decoyname=='tomcat':
      formatted_data[host]['Processes'][0]['Properties']=['rfi']
    elif decoyname=='femitter':
      formatted_data[host]['Processes'][0]['Username']='SYSTEM'
    elif decoyname=='HarakaSMPT': 
      formatted_data[host]['Processes'][0]['Service Name']='haraka'
    return formatted_data


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
    formatted_data = self.get_success_status(data)
    for key, value in data.items():
        if key != "success":
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

  def extract_tcp_pid(self,ip_string): 
      pattern = r'pid=(\d+)'
      pids = re.findall(pattern, data_string)
      print("Extracted PIDs:", pids)
      return pids 

  def parse_tcp(self,string):
      pattern = re.compile("(\\d+\\.\\d+\\.\\d+\\.\\d+)(?:.*?):\d+")
      pos = 0
      match = pattern.search(my_string, pos)
      ip_dict={}
      while match is not None:
        print('Group 0 is:',match.group(0),'group1:',match.group(1))
        ip_info= match.group(0)
        parts=ip_info.split(':')
        print('Parts:', parts)
        ip_dict[match.group(1)]=parts[1]
        pos = match.end(0)
        match = pattern.search(my_string, pos)
        print('match is',match)
      print(ip_dict)
      return ip_dict
  
  # Convert the Exploit remote services data to the required format
  def transform_ExploitRemoteService(self,data):
        if data['success']==False: 
           formatted_data = {}
           for key, value in data.items():
             if key == "success":
                   formatted_data[key] = self.get_success_status(data)
             else:
                ip=data['host_ip']
                formatted_data['1'] ={
            'Interface': [{'IP Address': IPv4Address(ip)}]
        }
                formatted_data[ip]= {
            'Interface': [{'IP Address': IPv4Address(ip)}],
            'Processes': [{
                'Connections': [{
                    'Status': 'ProcessState.OPEN',
                    'local_address': IPv4Address(ip),
                    'local_port': 21     #To Do: change it to Attacked port
                }],
                'Process Type': 'ProcessType.FEMITTER'
            }]
        }

        if data['success']== True:
           formatted_data = {}
           for key, value in data.items():
              if key == "success":
                formatted_data[key] = self.get_success_status(data)
              else: 
                exploit=data["available_exploit"]
                ip_string=data['ip_info']
                ip_dict=self.parse_tcp(ip_string)
                ip=data['host_ip']
                port= ip_dict[ip]

                alt_name= self.name_conversion.fetch_alt_name(ip)
                port_for_reverse_shell= port
                remote_port_on_attacker= 4444
                attacker_node= self.name_conversion.fetch_alt_name('User0')
                formatted_data[alt_name]= {
            'Processes': [
               {
                'Connections': [
                    {
                        'local_port': port_for_reverse_shell,
                        'remote_port': remote_port_on_attacker,
                        'local_address': IPv4Address(alt_name),
                        'remote_address': IPv4Address(attacker_node)
                    }
                ],
                'Process Type': 'ProcessType.REVERSE_SESSION'
               },
               {
                'Connections': [
                    {
                        'local_port': port,
                        'local_address': IPv4Address(alt_name),
                        'Status': 'ProcessState.OPEN'
                    }
                ],
                'Process Type': 'ProcessType.XXX'
               }
               ],
            'Interface': [{'IP Address': IPv4Address(alt_name)}],
            'Sessions': [{'ID': 1, 'Type': 'SessionType.RED_REVERSE_SHELL', 'Agent': 'Red'}],
            'System info': {'Hostname': self.action_param, 'OSType': 'OperatingSystemType.WINDOWS'}
             }
                formatted_data[attacker_node]={
              'Processes': [
                {
                'Connections': [
                    {
                        'local_port': remote_port_on_attacker,
                        'remote_port': port_for_reverse_shell,
                        'local_address': IPv4Address(attacker_node),
                        'remote_address': IPv4Address(alt_name)
                    }
                ],
                'Process Type': 'ProcessType.REVERSE_SESSION'
               }]
               }
                

        return formatted_data
 
  # Convert the Exploit remote services data to the required format
  def transform_PrivilegeEscalate(self,data):
    formatted_data = {}
    if data['success']== False: 
          formatted_data[key] = self.get_success_status(data) 
    elif data['success']==True: 
      for key, value in data.items():
        if key == "success":
          formatted_data[key] = self.get_success_status(data)
        else: 
           user=data["user"]
           explored_ip=data['explored_host']
           pid_string= data[pid_sting]
           pids= self.extract_tcp_pid(pid_string)
           subnet='10.1.1.234/24'
           host=data['action_param']
           data[host] = {
        'Sessions': [
            {
                'Username': user,
                'ID': 1,  # Assuming ID is static for this example
                'Timeout': 0,  # Assuming Timeout is static for this example
                'PID': pids[0],
                'Type': 'SessionType.RED_REVERSE_SHELL',
                'Agent': 'Red'
            }
        ],
        'Processes': [
            {
                'PID': pid,
                'Username': user
            }
        ],
        'Interface': [
            {
                'Interface Name': 'eth0',
                'IP Address': ipaddress.IPv4Address(host),
                'Subnet': ipaddress.IPv4Network(subnet)
            }
        ]
    }
    if explored_ip!= None:
     data[explored_ip] = {
        'Interface': [
            {
                'IP Address': ipaddress.IPv4Address(explored_ip)
            }
        ]
      }
           
    
    return formatted_data



class name_conversion():
   def __init__(self,path):
     with open(path,'r') as f:
         self.data = yaml.safe_load(f)
     print('Data is:',self.data)
     
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





