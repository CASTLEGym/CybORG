import pandas as pd
import matplotlib.pyplot as plt

# Load the data sets
sim_data = pd.read_csv('./cardiff_sim_actions_and_observations.csv')
emu_data = pd.read_csv('./cardiff_emu_actions_and_observations.csv')
team= 'cardiff'

# Display the first few rows of each data set to understand their structure
sim_data_head = sim_data.head()
emu_data_head = emu_data.head()

sim_data_head, emu_data_head



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

blue_sim_actions, blue_sim_avg_rewards, red_sim_actions, red_sim_avg_rewards, blue_emu_actions, blue_emu_avg_rewards, red_emu_actions, red_emu_avg_rewards



sim_total_reward = round(sim_data['Blue Reward'].sum(),2)
emu_total_reward= round(emu_data['Blue Reward'].sum(),2)
print(f"Total rewards in sim': {sim_total_reward}, emu {emu_total_reward}")



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

