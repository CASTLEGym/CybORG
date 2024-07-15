import pandas as pd
import matplotlib.pyplot as plt

# Load the data sets
sim_data = pd.read_csv('./dart_ne_sim_actions_and_observations.csv')
emu_data = pd.read_csv('./dart_ne_emu_actions_and_observations.csv')
team= 'dart_ne'
agent='Red'

# Display the first few rows of the data to understand the structure
print("Simulation Data:")
print(sim_data.head())
print("\nEmulation Data:")
print(emu_data.head())

"""
# Extract actions taken by red agents
sim_red_actions = sim_data[sim_data['agent'] == 'red']['action']
emu_red_actions = emu_data[emu_data['agent'] == 'red']['action']

# Count the occurrences of each action
sim_action_counts = sim_red_actions.value_counts()
emu_action_counts = emu_red_actions.value_counts()

# Create a DataFrame to facilitate plotting
actions_df = pd.DataFrame({
    'sim': sim_action_counts,
    'emu': emu_action_counts
}).fillna(0)  # Fill NaNs with 0 for actions not present in one of the datasets

# Plot the bar chart
actions_df.plot(kind='bar', figsize=(12, 8))
plt.title('Actions Taken by Red Agents in Simulation (sim) vs Emulation (emu)')
plt.xlabel('Actions')
plt.ylabel('Frequency')
plt.legend(title='Environment')
plt.xticks(rotation=45)
plt.grid(axis='y')

# Show the plot
plt.tight_layout()
plt.show()
"""






# Function to summarize action frequencies and average rewards for a given dataset
def summarize_actions_and_rewards(data, agent):
    actions = data[f'{agent} Action'].value_counts()
    avg_rewards = data.groupby(f'{agent} Action')[f'{agent} Reward'].mean()
    return actions, avg_rewards

# Summarize for both agents in both datasets
blue_sim_actions, blue_sim_avg_rewards = summarize_actions_and_rewards(sim_data, 'Blue')
red_sim_actions, red_sim_avg_rewards = summarize_actions_and_rewards(sim_data, 'Red')
blue_emu_actions, blue_emu_avg_rewards = summarize_actions_and_rewards(emu_data, 'Blue')
red_emu_actions, red_emu_avg_rewards = summarize_actions_and_rewards(emu_data, 'Red')

print(blue_sim_actions, type(blue_sim_actions))

blue_sim_avg_rewards, red_sim_actions, red_sim_avg_rewards, blue_emu_actions, blue_emu_avg_rewards, red_emu_actions, red_emu_avg_rewards



sim_total_reward = round(sim_data['Blue Reward'].sum(),2)
emu_total_reward= round(emu_data['Blue Reward'].sum(),2)
print(f"Total rewards in sim': {sim_total_reward}, emu {emu_total_reward}")



# Create a DataFrame to facilitate plotting
actions_df = pd.DataFrame({
    'sim': blue_sim_actions,
    'emu': red_emu_actions
})




# Plot the bar chart
actions_df.plot(kind='bar', figsize=(12, 8))
plt.title('Actions Taken by Red Agents in Simulation (sim) vs Emulation (emu)')
plt.xlabel('Actions')
plt.ylabel('Frequency')
plt.legend(title='Environment')
plt.xticks(rotation=90)
plt.grid(axis='y')

# Show the plot
plt.tight_layout()
plt.show()






# Plotting rewards as a function of iteration for Red agent in both sim and emu data
def plot_rewards_over_iterations(sim_data, emu_data, agent):
    fig, ax = plt.subplots(figsize=(15, 6))
    plt.annotate(f"-> Total reward in sim: {sim_total_reward}", (2.5, -0.5), textcoords="offset points", xytext=(0,1), ha='center', color='red')
    plt.annotate(f"-> Total reward in emu: {emu_total_reward}", (2.5, -0.45), textcoords="offset points", xytext=(0,1), ha='center', color='blue')
    ax.plot(sim_data['Iteration'], sim_data[f'{agent} Reward'], label='Simulation', color='red', alpha=0.7)
    ax.plot(emu_data['Iteration'], emu_data[f'{agent} Reward'], label='Emulation', color='blue', alpha=0.7)
    
    ax.set_title(f'{agent} Rewards Over Iterations')
    ax.set_xlabel('Iteration')
    ax.set_ylabel('Reward')
    ax.legend()
    # Save the plot as a PDF
    figname= team+'_agent_rewards.pdf'
    plt.savefig(figname)
    plt.show()
    

# Plot rewards for Red agent
plot_rewards_over_iterations(sim_data, emu_data, 'Blue')

