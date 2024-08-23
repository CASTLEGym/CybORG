from Wrappers.ChallengeWrapper2 import ChallengeWrapper2
from enum import Enum

# changed to ChallengeWrapper2
def wrap(env,team):
   if team=='cardiff' or team=='dart_ne':
     return ChallengeWrapper2(env=env, agent_name='Blue')
   elif team=='keep':
     return GraphWrapper('Blue', env)
   elif team == 'punch':
     return ActionWrapper(ObservationWrapper(RLLibWrapper(env=env, agent_name="Blue")))
      
def load_data_from_file(file_path):
    data_list = []
    with open(file_path, 'r') as file:
        for line in file:
            line = line.replace("\n", "")
            data_list.append(line)
    return data_list  


class load_ipmap_data:
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


def replace_ip_to_name(action_string):
    
    print('** Action string is:',action_string)
    split_action_string=action_string.split(" ")
    
    #if action contains the hostname
    if len(split_action_string)==2:
      action_param= split_action_string[1]
      action_name=split_action_string[0]
     
      #print("\n in vu_emu=> Action name:",action_name,";action parameter is:",action_param)
      is_host_name= is_name(action_param)
      if is_host_name == False:
        #print("** True host name **") 
        action_param= ip_to_host.fetch_alt_name(action_param)
        print("\n=> action name:: -",action_name, '; action param-',action_param)
        print('tot:',action_name+' '+action_param)
        return action_name +' '+action_param 
      else: 
        return action_string  
      
class TrinaryEnum(Enum):
    TRUE = 1
    FALSE = 0
    UNKNOWN = -1

def enum_to_boolean(enum_value):
    if enum_value == 'TRUE':
        return True
    elif enum_value == 'FALSE':
        return False
    else:
        return None

def generate_ports(num=50,min=4000,max=5000):
  return random.sample(range(min, max + 1), num)