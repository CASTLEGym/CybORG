import yaml

class cage2_os():
   def __init__(self,path="./assets/cage2-openstack.yaml"):
     with open(path,'r') as f:
         self.data = yaml.safe_load(f)
     #print('Data is:',self.data)
     
   def fetch_os_name(self,cage2_name='User0'):
     # Specify the key you want to read
     key_to_read = cage2_name
     # Check if the key exists before accessing its value
     if key_to_read in self.data:
        value = self.data[key_to_read]
        print(f"The value of '{key_to_read}' is: {value}")
     else:
        print(f"Key '{key_to_read}' not found in the YAML data.")
     return value
   
       
if __name__=='__main__':
   c2o=cage2_os()
   c2o.fetch_os_name() 

   


