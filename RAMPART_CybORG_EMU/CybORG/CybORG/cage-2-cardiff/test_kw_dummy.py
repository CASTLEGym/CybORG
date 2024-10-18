import requests

# Base URL of your Flask app
url = 'http://127.0.0.1:5000'


# Fetch action_space
response = requests.get(f'{url}/action_space')
print(response.json())

# Fetch observation_space
response = requests.get(f'{url}/observation_space')
print(response.json())

# Fetch action_mapping_dict
response = requests.get(f'{url}/action_mapping_dict')
print(response.json())


# Invoke the 'reset' method with x=10 and y=5
response = requests.get(f'{url}/rampart/make', params={'x': 10})
print(response.json())

# Invoke the 'reset' method with x=10 and y=5
response = requests.get(f'{url}/rampart/reset', params={'x': 10, 'y': 5})
print(response.json())

# Invoke the 'step' method with x=4 and y=2
response = requests.get(f'{url}/rampart/step', params={'x': 4, 'y': 2})
print(response.json())





# Invoke the 'close' method
response = requests.get(f'{url}/rampart/close')
print(response.json())
