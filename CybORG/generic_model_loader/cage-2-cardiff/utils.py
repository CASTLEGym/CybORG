import json 
import os
import yaml

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
