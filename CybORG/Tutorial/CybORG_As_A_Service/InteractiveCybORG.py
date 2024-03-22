from CybORG import CybORG, CYBORG_VERSION

from CybORG.Agents import B_lineAgent, BlueReactRestoreAgent, BlueReactRemoveAgent, \
    RandomAgent, RedMeanderAgent, SleepAgent
from CybORG.Agents.MainAgent import MainAgent

from CybORG.Agents.Wrappers.ChallengeWrapper import ChallengeWrapper
from CybORG.Agents.Wrappers import EnumActionWrapper
from CybORG.Agents.Wrappers.FixedFlatWrapper import FixedFlatWrapper
from CybORG.Agents.Wrappers.IntListToAction import IntListToActionWrapper
from CybORG.Agents.Wrappers.OpenAIGymWrapper import OpenAIGymWrapper
from CybORG.Simulator.Scenarios.FileReaderScenarioGenerator import FileReaderScenarioGenerator

from CybORG.Tutorial.GameStateManager import GameStateManager

class InteractiveCybORG:
    def __init__(self, num_steps, red_agent_type):
        self.cyborg = None
        self.game_id = None
        self.num_steps = num_steps
        self.red_agent_type = red_agent_type
        self.game_state_manager = GameStateManager()
        self.agent = BlueReactRemoveAgent()  # Change this line to load your agent


    def configure(self, args):
        path = str(inspect.getfile(CybORG))[:-7] + '/Simulator/Scenarios/scenario_files/Scenario2.yaml'
        sg = FileReaderScenarioGenerator(path)
        red_agent = self.red_agent_type()
        self.cyborg = CybORG(sg, 'sim', agents={'Red': red_agent})
        self.game_state_manager.set_environment(
            cyborg=self.cyborg,
            red_agent=red_agent,
            blue_agent=self.agent,
            num_steps=self.num_steps)

    
    def run_step(self, step_num):
        if not self.cyborg:
            self.setup()
        
        blue_action_space = self.cyborg.get_action_space('Blue')
        blue_obs = self.cyborg.get_observation('Blue')  # get the newest observation
        blue_action = self.agent.get_action(blue_obs, blue_action_space)
        result = self.cyborg.step('Blue', blue_action, skip_valid_action_check=False)

        state_snapshot = self.game_state_manager.create_state_snapshot()
        self.game_state_manager.store_state(state_snapshot, step_num, self.num_steps)

        # Return the current state, rewards, actions, etc., as needed
        return state_snapshot

    
    def reset(self):
        self.cyborg.reset()
        self.game_state_manager.reset()

