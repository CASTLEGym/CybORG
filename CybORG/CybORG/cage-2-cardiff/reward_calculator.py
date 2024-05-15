
import yaml
class RewardCalculator():
    # this reward calculator provides a reward to both red and blue due to changes in the number of privileged sessions
    def __init__(self, scenario):
        self.old_total = 0

        self.mapping = {'None': 0.0,
                        'Low': 0.1,
                        'Medium': 1.0,
                        'High': 10.0}
        self.compromised_hosts = {}
        with open(scenario, 'r') as file:
            # Load the YAML content
            self.scenario = yaml.safe_load(file)
        print('Scenario data is:',self.scenario)
    def reset(self):
        self.old_total = 0


    def privilegedrewardcalculator(self,current_state:dict):
        root_sessions=0; system_sessions=0
        for host, info in current_state.items():

            if host == 'success':
                continue

            if 'Sessions' in info:
                for session in info['Sessions']:
                        #if session['Agent'] == self.agent_name:
                        # count the number of root sessions
                        if session['Username'] == 'root' and info['System info']['OSType'] == 'LINUX':
                            confidentiality_value = self.mapping[self.scenario.get('Hosts', {}).get(host, {}).get('ConfidentialityValue', 'Low')]
                            root_sessions += confidentiality_value
                            self.compromised_hosts[host] = confidentiality_value
                            break
                        # count the number of SYSTEM sessions
                        if session['Username'] == 'SYSTEM' and info['System info']['OSType'] == 'WINDOWS':
                            confidentiality_value = self.mapping[self.scenario.get('Hosts', {}).get(host, {}).get('ConfidentialityValue', 'Low')]
                            system_sessions += confidentiality_value
                            self.compromised_hosts[host] = confidentiality_value
                            break

            # find the difference from the old privileged sessions
        total = root_sessions + system_sessions
        reward = total  # - self.old_total
        self.old_total = total
        return round(reward, 3)

    def reward(self,observation):
        reward= self.privilegedrewardcalculator(observation)
        return [-1*reward,reward]   #[Blue reward, red rewards]


if __name__=='__main__':
    reward_cal=RewardCalculator('/home/lab_linux/harsh/CAGE_RL/CybORG_wrapper/CybORG/CybORG/Shared/Scenarios/Scenario2.yaml')
    obs= {"success":"True/False/Unknown", 'Op_Server0':{'Sessions':[{'Username':'root', 'ID': 0,'Timeout':0,'PID':2323}],'System info': {'OSType':'LINUX'}}, 'User1':{'Sessions':[{'Username':'root', 'ID': 0,'Timeout':0,'PID':2323}],'System info': {'OSType':'LINUX'}},'Enterprise1': {'Interface': [{'IP Address': '10.0.120.158'}]}}

    reward=reward_cal.reward(obs)
    print(reward)
    print('Done')
