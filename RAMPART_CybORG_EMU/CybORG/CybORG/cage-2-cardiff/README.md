# Version 0 : 

Testing end to end execution of emulation actions and wrapper integration.

Target: Tranforming actions to emulation and getting observation back from emulation to cyborg. The thorough analysis of extact match if possible.  

#### New ENV class: 
- It takes parameter as a json string in follwoing format: 
   '{
     "mode": "sim"
     "scenario": "Scenario2.yaml",
     "main_agent": "Blue",              
     "red_agent": "B_lineAgent",
     "green_agent": "SleepAgent",
     "wrapper": "ChallengeWrapper",
     "episode_length": EPS_LEN,
     "max_episodes": MAX_EPS,
     "seed": 0
   }'
  

  The `main_agent` defines the agent that is going to steer the game. The other agent is loaded as prebuilt like `B_lineAgent` or `cardiff` agent. In future it may support two main_agents (Blue as well as Red).