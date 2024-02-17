import sys
import argparse
import yaml
status_file_path= 'status.yaml'
success_probability=0.9
import random
seed_value = 42
random.seed(seed_value)
import os

class ActionExecutor:

    def __init__(self, action,param):
        self.action_name = action
        self.action_param = param


    def read_yaml_file(self,file_path):
      """
      Reads a YAML file from the specified path and returns its contents.

      Parameters:
      file_path (str): The path to the YAML file.

      Returns:
      dict: The contents of the YAML file.
      """
      try:
        with open(file_path, 'r') as file:
            return yaml.safe_load(file)
      except Exception as e:
        return {"error": str(e)}
  

    def append_to_yaml(self,file_path, key, value):
      """ 
      Usage:
      # Specify the file path, key, and value
      file_path = '/path/to/your/file.yaml'
      key = 'MODIFY'
      value = 'Test_Value'

      # Call the function to append to the YAML file
      append_to_yaml(file_path, key, value)
      """
      # Load existing YAML data.
      try:
        with open(file_path, 'r') as file:
            data = yaml.safe_load(file)
      except FileNotFoundError:
        # If the file doesn't exist, create an empty data structure.
        data = {}

      # Add or update the key-value pair.
      data[key] = value

      # Write the modified data back to the YAML file.
      with open(file_path, 'w') as file:
        yaml.dump(data, file, default_flow_style=False)


    def extract_pid_port_process_name(self,host_info):
      """
      Extracts the PIDs, ports, and process names from the Processes section of the given host info.

      Parameters:
      host_info (dict): Dictionary containing host information.

      Returns:
      list of tuples: A list of tuples, each containing PID, port, and process name.
      """
      process_details = []
      processes = host_info.get('Processes', [])
    
      for process in processes:
        pid = process.get('PID')
        process_name = process.get('Process Name')
        ports = [conn['local_port'] for conn in process.get('Connections', []) if 'local_port' in conn]

        for port in ports:
            process_details.append((pid, port, process_name))

      return process_details


    def extract_ports(self,host_info):
      """
      Extracts the ports from the Processes section of the given host info.

      Parameters:
      host_info (dict): Dictionary containing host information.

      Returns:
      list of tuples: A list of ports.
      """
      port_details = []
      processes = host_info.get('Processes', [])
    
      for process in processes:
        #pid = process.get('PID')
        #process_name = process.get('Process Name')
        ports = [conn['local_port'] for conn in process.get('Connections', []) if 'local_port' in conn]

        for port in ports:
            port_details.append((port))

      return port_details


    
    ##############################
    ####### Blue actions  ########
    ############################## 

    def DecoyApache(self):
      service_name= "apache2"
      local_port=80
      local_address='0.0.0.0'
      properties='rfi'
      process_type='webserver'
      path='/usr/sbin'
      content=self.read_yaml_file('config.yaml')
      ports=self.extract_ports(content)
      if local_port in ports:
        return self.create_decoy(service_name,local_port,local_address,properties,process_type,path)
      else:
        return False

    def DecoySSHD(self):
      service_name= "sshd"
      local_port=22
      local_address='0.0.0.0'
      properties= None 
      process_type='sshd'
      path="C:\\Program Files\\OpenSSH\\usr\\sbin"
      return self.create_decoy(service_name,local_port,local_address,properties,process_type,path)
      content=self.read_yaml_file('config.yaml')
      ports=self.extract_ports(content)
      if local_port in ports:
        return False
      else:
        return self.create_decoy(service_name,local_port,local_address,properties,process_type,path)
        

    def DecoyVsftpd(self):
      service_name= "vsftpd"
      local_port=80
      local_address='0.0.0.0'
      properties='rfi'
      process_type='webserver'
      path='/usr/sbin'
      return self.create_decoy(service_name,local_port,local_address,properties,process_type,path)
      content=self.read_yaml_file('config.yaml')
      ports=self.extract_ports(content)
      if local_port in ports:
        return False
      else:
        return self.create_decoy(service_name,local_port,local_address,properties,process_type,path)
   
    def DecoyFemitter(self):
      service_name= "femitter"
      local_port=21
      local_address='0.0.0.0'
      properties= None 
      process_type='femitter'
      path='/usr/sbin'
      return self.create_decoy(service_name,local_port,local_address,properties,process_type,path)
      content=self.read_yaml_file('config.yaml')
      ports=self.extract_ports(content)
      if local_port in ports:
        return False
      else:
        return self.create_decoy(service_name,local_port,local_address,properties,process_type,path)

    def DecoyTomcat(self):
      service_name= "tomcat"
      local_port=443
      local_address='0.0.0.0'
      properties='rfi'
      process_type='webserver'
      path=None
      return self.create_decoy(service_name,local_port,local_address,properties,process_type,path)
      content=self.read_yaml_file('config.yaml')
      ports=self.extract_ports(content)
      if local_port in ports:
        return False
      else:
        return self.create_decoy(service_name,local_port,local_address,properties,process_type,path)
    
    def DecoyHarakaSMPT(self):
      service_name= "haraka"
      local_port=25
      local_address='0.0.0.0'
      properties= None 
      process_type='smtp'
      path='/usr/sbin'
      return self.create_decoy(service_name,local_port,local_address,properties,process_type,path)
      content=self.read_yaml_file('config.yaml')
      ports=self.extract_ports(content)
      if local_port in ports:
        return False
      else:
        return self.create_decoy(service_name,local_port,local_address,properties,process_type,path)

    def create_decoy(self,service_name,local_port,local_address,properties,process_type,path):
      # To do : 
      # check if the port is free (from both config and status file). Deploy decoy only if the port is free.
      # Load existing YAML data.
      with open(status_file_path, 'r') as file:
            data = yaml.safe_load(file)
      if data==None:
        # If the file doesn't exist, create an empty data structure
        data = {}
    
      # Add or update the key-value pair.
      data[service_name]= {}
      data[service_name]['local_port'] = local_port 
      data[service_name]['local_address'] = local_address 
      data[service_name]['properties'] = properties 
      data[service_name]['process_type'] = process_type
      data[service_name]['path'] = path
      # Write the modified data back to the YAML file.
      with open(status_file_path, 'w') as file:
        yaml.dump(data, file, default_flow_style=False)
      return True
      
    def Restore(self): 
      # Clean the status file to the fresh one.
      with open(status_file_path, 'w') as file:
        file.truncate()
      return True
      
    def Remove(self):
      # Kill the suspicious reverse shell processes started by the red agent.
      target_port='reverse_shell'
      with open(status_file_path, 'r') as file:
            data = yaml.safe_load(file)
      #print("Data is:",data)
      if data!= None: 
        cleaned_data = {key: value for key, value in data.items() if value.get('process_name') != target_port}
        with open(status_file_path, 'w') as file:
          yaml.dump(cleaned_data, file, default_flow_style=False)
      return True 


    ##############################
    ####### Red actions  ########
    ############################## 

    def PrivilegeEscalate(self):
      if random.random()>success_probability:
        return True
      else:
        return False
   
    def ExploitRemoteService(self):
      # Check valid exploits and execute them.
      available_exploits=["EternalBlue","BlueKeep","HTTPRFI","HTTPSRFI","SSHBruteForce","SQLInjection","HarakaRCE","FTPDirectoryTraversal"]
      if self.exploit_name in available_exploits:
       if random.random()>success_probability:
        with open(status_file_path, 'r') as file:
            data = yaml.safe_load(file)
        if data==None:
          # If the file doesn't exist, create an empty data structure
          data = {}
        #print(self.exploit_name)
        # Add or update the key-value pair
        data[self.exploit_name]= {}
        data[self.exploit_name]['file_density'] = 0.9 
        data[self.exploit_name]['file_signed'] = False 
        data[self.exploit_name]['process_name'] = 'reverse_shell'
        data[self.exploit_name]['port'] = random.randint(4000, 5000)
        with open(status_file_path, 'w') as file:
          yaml.dump(data, file, default_flow_style=False)
        return True
       else:
        return False
      else: 
        return False
    
    
    def dummy_nmap(self):
       pass
    
    def DiscoverRemoteSystems(self):
      # replaced by nmap string and invoked using subprocess , wait for result and parse the nmap output in desired template
      config_file_name= 'config'+self.action_param+'.yaml'
      parsed_yaml = self.read_yaml_file(config_file_name)
      #print(parsed_yaml)
      #print(parsed_yaml)
      subnet = self.action_param
      hosts = {entry.split(':')[1] for entry in parsed_yaml['Hosts']}
      ###
      ##possible nmap string for all above code
      #data_raw=namp self.action_param
      #parse data_raw in data template
      
      
      # Create the desired dictionary
      data = {
          "success": True,
           subnet: hosts
             }
      return data
    
    
    def DiscoverNetworkServices(self):
      # return PID,port,process_name on a host
      # replaced by nmap string and invoked using subprocess , wait for result and parse the nmap output in desired template
      config_file_name= 'config'+self.action_param+'.yaml'
      parsed_yaml = self.read_yaml_file(config_file_name)
      print(parsed_yaml)
      key = self.action_param
      value = self.extract_ports(parsed_yaml)
      ###
      ##possible nmap string for all above code
      #data_raw=namp self.action_param
      #parse data_raw in data template
      
      # Create the desired dictionary
      data = {
          "success": True,
           key: value
             }
      print('data is:',data)
      return data

     

if __name__=='__main__':
  
  parser = argparse.ArgumentParser(
        prog="action_executor.py",
        description="Execute an action on the client host"
    )
  parser.add_argument(
        "action_name",
        nargs="?",
        default="Restore",
        help="Action that needs to be executed, default is Restore."
    )
    
  parser.add_argument(
        "action_param",
        nargs="?",
        default=None,
        help="The action param, default is None."
    )

  args = parser.parse_args()
  if len(args.action_name) == 0 :
        print(f"{sys.argv[0]}:  Action name not defined ")
        sys.exit(1)

  execute_action = ActionExecutor(args.action_name, args.action_param)
  result=execute_action.DiscoverRemoteSystems()
  
  #print(args.action_name,args.exploit_name )
  
  #foo= getattr(execute_action,args.action_name,arg.action_param)
  #result= foo() 
  #print('from action executor::::::;')
  print(result)
  
