from flask import Flask, jsonify, request, redirect, url_for
import argparse
from rampart_env import setup_openstack
from rampart_env import rampart_emulator

# Initialize Flask application
app = Flask(__name__)

# Placeholder Class for the front end, will be filled with by the actual classes and parameters.
class rampart_emu:
    def __init__(self):
        # Exposed attributes need to fill it by running emulation.
        self.action_space = "Intial placeholder for action space"  # Class attribute for version
        self.observation_space = 'Intial placeholder for observation space'
        self.action_mapping_dict = 'Intial placeholder for action mapping'
        self.env = rampart_emulator()  # Placeholder for environment

    def make(self, game_param):
        # KW docs ###
        # Input:: game param  (json)
        # Returns: None ( we are returing True and False abot success)
        print('calling make!')
        # Currnelty just making placeholder for action space and observation space
        success=self.env.make(game_param)
        return success

    def reset(self, seed=0, agent='Blue'):
        # KW docs ###
        # Input:: seed: int or None; agent: str or AgentType or None 
        # Returns: action_space, observation_space,intial_obs, action_mapping_dict - Blue, Red.
        action_space,observation_space, obs, self.action_mapping_dict=self.env.reset(seed,agent)

        return action_space,observation_space, obs, self.action_mapping_dict

    def step(self, x, y):
        # KW docs ###
        # Inputs: x: int or str (action); y: str or AgentType 
        # Returns: observation (ObsType), rewards (float), terminated (bool), truncated (bool), info (dict), done (bool)
        return x * y

    def close(self):
        # KW docs ###
        # Inputs: None
        # Returns: done (bool)
        return True


# Instantiate the class
rampart_env = rampart_emu()


# Root route that opens when the browser accesses the base URL
@app.route('/')
def index():
    # Welcome msg
    return jsonify('Welcome to RAMPART emulation environment!')


# API route to return the action_space attribute
@app.route('/action_space', methods=['GET'])
def get_action_space():
    return jsonify({
        "action_space": rampart_env.action_space
    })


# API route to return the observation_space attribute
@app.route('/observation_space', methods=['GET'])
def get_observation_space():
    return jsonify({
        "observation_space": rampart_env.observation_space
    })


# API route to return the action_mapping_dict attribute
@app.route('/action_mapping_dict', methods=['GET'])
def get_action_mapping_dict():
    return jsonify({
        "action_mapping_dict": rampart_env.action_mapping_dict
    })


# Static API route for `make` method
@app.route('/rampart/make', methods=['POST'])
def make():
    if request.is_json:
        game_param = request.get_json()
        result = rampart_env.make(game_param)
        return jsonify({"operation": "make", "result": result})
    else:
        return jsonify({"error": "Invalid input. Expected JSON."}), 400


# Static API route for `reset` method
@app.route('/rampart/reset', methods=['GET'])
def reset():
    seed = request.args.get('seed', type=int)
    agent = request.args.get('agent', type=str)
    if seed is not None and agent is not None:
        result = rampart_env.reset(seed, agent)
        return jsonify({"operation": "reset", "result": result})
    else:
        return jsonify({"error": "Invalid input. seed and agent are required."}), 400


# Static API route for `step` method
@app.route('/rampart/step', methods=['GET'])
def step():
    x = request.args.get('x', type=float)
    y = request.args.get('y', type=float)
    if x is not None and y is not None:
        result = rampart_env.step(x, y)
        return jsonify({"operation": "step", "result": result})
    else:
        return jsonify({"error": "Invalid input. x and y are required."}), 400


# Static API route for `close` method
@app.route('/rampart/close', methods=['GET'])
def close():
    result = rampart_env.close()
    return jsonify({"operation": "close", "result": result})


# Function to handle command-line arguments
def parse_args():
    parser = argparse.ArgumentParser(description='Flask App to perform calculations via REST API')

    # Port argument (default is 5000)
    parser.add_argument('--port', type=int, default=5000, help='Port to run the Flask app on (default: 5000)')

    # SSL argument (optional)
    parser.add_argument('--ssl', action='store_true', help='Enable SSL with self-signed certificates (requires cert.pem and key.pem)')

    # Debug argument (optional)
    parser.add_argument('--debug', action='store_true', help='Enable debugging mode')

    return parser.parse_args()


# Run the app when the script is executed
if __name__ == '__main__':
    # Parse command-line arguments
    args = parse_args()

    # Check if SSL is enabled
    if args.ssl:
        ssl_context = ('cert.pem', 'key.pem')
    else:
        ssl_context = None

    # Run the Flask app with parsed arguments
    app.run(port=args.port, debug=args.debug, ssl_context=ssl_context)
