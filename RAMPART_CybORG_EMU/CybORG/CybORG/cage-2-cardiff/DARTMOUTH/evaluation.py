import subprocess
import inspect
import time
from statistics import mean, stdev

from CybORG import CybORG, CYBORG_VERSION
from CybORG.Agents import B_lineAgent, SleepAgent
from CybORG.Agents.SimpleAgents.Meander import RedMeanderAgent
from Wrappers.ChallengeWrapper2 import ChallengeWrapper2
from Agents.MainAgent import MainAgent
import random

MAX_EPS = 1
agent_name = 'Blue'
random.seed(0)


# changed to ChallengeWrapper2
def wrap(env):
    return ChallengeWrapper2(env=env, agent_name='Blue')

def get_git_revision_hash() -> str:
    return subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('ascii').strip()

if __name__ == "__main__":
    
    scenario = 'Scenario2'
    

    lines = inspect.getsource(wrap)
    wrap_line = lines.split('\n')[1].split('return ')[1]
    print(wrap_line)
    # Change this line to load your agent
    agent = MainAgent()

    print(f'Using agent {agent.__class__.__name__}, if this is incorrect please update the code to load in your agent')

    
    path = str(inspect.getfile(CybORG))
    path = path[:-10] + f'/Shared/Scenarios/{scenario}.yaml'

    for num_steps in [100]:
        for red_agent in [B_lineAgent]:
            
            cyborg = CybORG(path, 'sim', agents={'Red': red_agent})
            wrapped_cyborg = wrap(cyborg)

            observation = wrapped_cyborg.reset()
            # observation = cyborg.reset().observation

            action_space = wrapped_cyborg.get_action_space(agent_name)
            # action_space = cyborg.get_action_space(agent_name)
            total_reward = []
            actions = []
            for i in range(MAX_EPS):
                r = []
                a = []
                # cyborg.env.env.tracker.render()
                for j in range(num_steps):
                    print('%%'*75,'iteration:',j)
                    action = agent.get_action(observation, action_space)
                    observation, rew, done, info = wrapped_cyborg.step(action)
                    # result = cyborg.step(agent_name, action)
                    r.append(rew)
                    # r.append(result.reward)
                    a.append((str(cyborg.get_last_action('Blue')), str(cyborg.get_last_action('Red'))))
                    print('%%'*75)
                agent.end_episode()
                total_reward.append(sum(r))
                actions.append(a)
                # observation = cyborg.reset().observation
                observation = wrapped_cyborg.reset()
            #print(f'Average reward for red agent {red_agent.__name__} and steps {num_steps} is: {mean(total_reward)} with a standard deviation of {stdev(total_reward)}')
            
            print(f'-> Total reward is {total_reward}, and stepwise rewards are {r}')
            print(f'-> action are {a}')
