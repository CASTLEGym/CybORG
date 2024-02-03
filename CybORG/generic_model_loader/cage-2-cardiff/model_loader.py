from Agents.MainAgent import MainAgent


class model_loader:
   def __init__(self):
    #Change this line to load your agent
    self.agent = MainAgent()
    print(f'Using agent {self.agent.__class__.__name__}, if this is incorrect please update the code to load in your agent')
    
   def get_action(self,observation,action_space):
     #print("Observation from model_loader is:",observation)
     action = self.agent.get_action(observation, action_space)
     #print('Action from model loader is:',action)
     return action
     
   def end_episode(self):
     self.agent.end_episode()
     
