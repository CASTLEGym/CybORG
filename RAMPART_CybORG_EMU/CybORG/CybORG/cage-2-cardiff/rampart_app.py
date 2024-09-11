from flask import Flask, jsonify, request
from rampart_env import rampart_emu

# Initialize Flask application
app = Flask(__name__)

# Class with multiple functions
class rampart_emu:
    def make(self, x, y):
        return x + y

    def reset(self, x, y):
        return x - y

    def step(self, x, y):
        return x * y

    def terminate(self, x, y):
        if y == 0:
            return "Division by zero is undefined"
        return x / y

# Instantiate the class
calculator = rampart_emu()

# API route to dynamically invoke class methods
@app.route('/calculate/<string:operation>', methods=['GET'])
def calculate(operation):
    try:
        # Extract parameters from query string
        x = float(request.args.get('x'))
        y = float(request.args.get('y'))
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid input. Please provide valid numbers for x and y."}), 400

    # Check if the requested operation exists in the class
    if hasattr(calculator, operation):
        # Get the method from the class by name
        method = getattr(calculator, operation)
        # Invoke the method with parameters and return the result
        result = method(x, y)
        return jsonify({"operation": operation, "result": result})
    else:
        # Return error if the operation is not supported
        return jsonify({"error": f"Operation '{operation}' not found."}), 400

# Run the app when the script is executed
if __name__ == '__main__':
    app.run(debug=True)
