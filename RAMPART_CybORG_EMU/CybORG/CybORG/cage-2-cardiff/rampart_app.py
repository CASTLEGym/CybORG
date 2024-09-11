from flask import Flask, jsonify, request, redirect, url_for
import inspect
import argparse

# Initialize Flask application
app = Flask(__name__)

# Dummy Class 
class rampart_emu:
    def __init__(self):
        self.action_space = "1.0"  # Class attribute for version
        self.observation_space = ["add", "subtract", "multiply", "divide"]
        self.action_mapping_dict= {'key':'value'}
        
    def make(self, x):
        return x 

    def reset(self, x, y):
        return x - y

    def step(self, x, y):
        return x * y

    def close(self):
        return x**2


# Instantiate the class
rampart_env = rampart_emu()


# Root route that opens when the browser accesses the base URL
@app.route('/')
def index():
    # Welcome msg
    return jsonify('Welcome to RAMPART emulation environment !')
    
# API route to return the attributes  action_space
@app.route('/action_space', methods=['GET'])
def get_action_space():
    return jsonify({
        "action_space": rampart_env.action_space
    })

# API route to return available attribute observation_space (class attribute)
@app.route('/observation_space', methods=['GET'])
def get_observation_space():
    return jsonify({
        "observation_sapce": rampart_env.observation_space
    })

# API route to return available attribute observation_space (class attribute)
@app.route('/action_mapping_dict', methods=['GET'])
def get_action_mapping_dict():
    return jsonify({
        "action_mapping_dict": rampart_env.action_mapping_dict
    })  
  
# API route to dynamically invoke class methods
@app.route('/rampart/<string:operation>', methods=['GET'])
def rampart(operation):
    if hasattr(rampart_env, operation):
        # Get the method by name
        method = getattr(rampart_env, operation)
        
        # Inspect the method signature to know the number of required arguments
        sig = inspect.signature(method)
        param_count = len(sig.parameters)
        
        # Extract parameters from request.args (query string)
        params = request.args
        
        # Check if enough parameters are provided
        if len(params) != param_count:
            return jsonify({"error": f"Operation '{operation}' requires {param_count} parameters."}), 400
        
        try:
            # Dynamically pass the correct number of parameters based on the method's signature
            args = [float(params[param_name]) for param_name in sig.parameters]
        except (TypeError, ValueError):
            return jsonify({"error": "Invalid input. Please provide valid numbers for the parameters."}), 400
        
        # Call the method with extracted arguments
        result = method(*args)
        return jsonify({"operation": operation, "result": result})
    else:
        return jsonify({"error": f"Operation '{operation}' not found."}), 400




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
    
    