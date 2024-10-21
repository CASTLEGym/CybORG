import requests

# Base URL of your Flask app
url = 'http://127.0.0.1:5000'

game_param = '{"mode":"emu","scenario": "Scenario2.yaml","main_agent": "Blue","red_agent": "B_lineAgent","green_agent": "SleepAgent","wrapper": "None", "episode_length": 1,"max_episodes": 1, "seed": 0}'
# Fetch action_space
response = requests.get(f'{url}/action_space')
print(response.json())

# Fetch observation_space
response = requests.get(f'{url}/observation_space')
print(response.json())

# Fetch action_mapping_dict
response = requests.get(f'{url}/action_mapping_dict')
print(response.json())


# The JSON payload to send to the `make` method
game_param = {
    "mode": "emu",
    "scenario": "Scenario2.yaml",
    "main_agent": "Blue",
    "red_agent": "B_lineAgent",
    "green_agent": "SleepAgent",
    "wrapper": "None",
    "episode_length": 1,
    "max_episodes": 1,
    "seed": 0
}

# Send a POST request with the JSON payload
response = requests.post(f'{url}/rampart/make', json=game_param)

# Print the response from the server
print(f"Status Code: {response.status_code}")
print("Response JSON:", response.json())


# Invoke the 'reset' method with x=10 and y=5
#print('calling reset!!')
#response = requests.get(f'{url}/rampart/reset', params={'seed': 10, 'agent': 'Blue'})
#print(response.json())

"""
# Invoke the 'step' method with x=4 and y=2
response = requests.get(f'{url}/rampart/step', params={'x': 4, 'y': 2})
print(response.json())

# Invoke the 'close' method
response = requests.get(f'{url}/rampart/close')
print(response.json())

"""