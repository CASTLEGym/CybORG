
## Initialize  GameStateCollector
```python
game_state_manager = GameStateCollector(environment='sim') # or 'emu' or anything you defined
```

## Set up GameStateCollector environment at the start of your episode
```python
game_state_manager.set_environment(cyborg=cyborg,
                                   red_agent=red_agent,
                                   blue_agent=agent,
                                   num_steps=num_steps)
game_state_manager.reset()
```

## Gather Actions & Observations Info after every step

```python
red_action: str 
blue_action: str

red_observation: dict
blue_observation: dict

actions = {"Red": red_action, "Blue": blue_action}
observations = {"Red": red_observation, "Blue": blue_observation}
```
For example:
```python
actions = {'Blue': 'Sleep', 'Red': 'ExploitRemoteService 10.0.190.38'}

observations = {'Blue': {'success': <TrinaryEnum.UNKNOWN: 2>},
                 'Red': {'10.0.162.119': {'Interface': [{'IP Address': IPv4Address('10.0.162.119')}],
                                          'Processes': [{'Connections': [{'local_address': IPv4Address('10.0.162.119'),
                                                                          'local_port': 4444,
                                                                          'remote_address': IPv4Address('10.0.190.38'),
                                                                          'remote_port': 59658}],
                                         'Process Type': <ProcessType.REVERSE_SESSION_HANDLER: 10>}]},
                         '10.0.190.38': {'Interface': [{'IP Address': IPv4Address('10.0.190.38')}],
                                         'Processes': [{'Connections': [{'Status': <ProcessState.OPEN: 2>,
                                                                         'local_address': IPv4Address('10.0.190.38'),
                                                                         'local_port': 443}],
                                                        'Process Type': <ProcessType.WEBSERVER: 7>},
                                                       {'Connections': [{'local_address': IPv4Address('10.0.190.38'),
                                                                         'local_port': 59658,
                                                                         'remote_address': IPv4Address('10.0.162.119'),
                                                                         'remote_port': 4444}],
                                                        'Process Type': <ProcessType.REVERSE_SESSION: 11>}],
                                         'Sessions': [{'Agent': 'Red',
                                                       'ID': 2,
                                                       'Type': <SessionType.RED_REVERSE_SHELL: 11>}],
                                         'System info': {'Hostname': 'Enterprise1',
                                                         'OSType': <OperatingSystemType.LINUX: 3>}},
                         'success': <TrinaryEnum.TRUE: 1>}}
```

## Create a state_snapshot of the current step

```python
state_snapshot = game_state_manager.create_state_snapshot(actions, observations)
```

## Store state_snapshot of the current step
```python
"""
i is the current episode number
j is the current step number

your for loop should taken care of this
"""

game_state_manager.store_state(state_snapshot, i, j)
```

## Reset after every episode ends
```python
game_state_manager.reset()
```

## Full Example
```python
def main(agent_type: str, cyborg_type: str, environment="sim") -> None:
    environment = environment
    cyborg_version = CYBORG_VERSION
    scenario = 'Scenario2'
    # ask for a name for the agent
    name_of_agent = "PPO + Greedy decoys"

    lines = inspect.getsource(wrap)
    wrap_line = lines.split('\n')[1].split('return ')[1]

    # Change this line to load your agent
    agent = MainAgent()
    
    path = str(inspect.getfile(CybORG))
    path = path[:-7] + f'/Simulator/Scenarios/scenario_files/Scenario2.yaml'
    sg = FileReaderScenarioGenerator(path)

    print(f'using CybORG v{cyborg_version}, {scenario}\n')
    
    # game manager initialization
    environment = 'sim'
    game_state_manager = GameStateCollector(environment=environment)
    
    for num_steps in [2]:
        for red_agent in [B_lineAgent]:
            red_agent = red_agent()
            cyborg = CybORG(sg, environment, agents={'Red': red_agent})
            wrapped_cyborg = wrap(cyborg)

            observation = wrapped_cyborg.reset()
            # observation = cyborg.reset().observation

            red_agent_name: str = red_agent.__class__.__name__
            blue_agent_name: str = agent.__class__.__name__
            
            # Set up game_state_manager
            game_state_manager.set_environment(cyborg=cyborg,
                                               red_agent_name=red_agent_name,
                                               blue_agent_name=blue_agent_name,
                                               num_steps=num_steps)
            game_state_manager.reset()

            action_space = wrapped_cyborg.get_action_space(agent_name)

            for i in range(MAX_EPS):
                r = []
                a = []
                
                # cyborg.env.env.tracker.render()
                for j in range(num_steps):
                    if environment == "sim":
                        action = agent.get_action(observation, action_space)
                        observation, rew, done, info = wrapped_cyborg.step(action)

                        actions = {"Red":str(cyborg.get_last_action('Red')), "Blue": str(cyborg.get_last_action('Blue'))}
                        observations = {"Red": cyborg.get_observation('Red'), "Blue": cyborg.get_observation('Blue')}
                        pprint(actions)
                        pprint(observations)

                    # Create state for this step
                    state_snapshot = game_state_manager.create_state_snapshot(actions, observations)
                    
                    game_state_manager.store_state(state_snapshot, i, j)
                    
                # game manager reset
                agent.end_episode()
                observation = wrapped_cyborg.reset()
                game_state_manager.reset()
                        
    return game_state_manager.get_game_state()
```
