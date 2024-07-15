import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV files
agent = 'Red'
agent1 = 'Blue'

#sim_data = pd.read_csv('dart_ne_sim_actions_and_observations.csv')
#emu_data = pd.read_csv('dart_ne_emu_actions_and_observations.csv')

sim_data = pd.read_csv('cardiff_sim_actions_and_observations.csv')
emu_data = pd.read_csv('cardiff_emu_actions_and_observations.csv')

# Extract relevant columns
sim_data_reduced_1 = sim_data[['Iteration', f'{agent} Action']]
emu_data_reduced_1 = emu_data[['Iteration', f'{agent} Action']]
sim_data_reduced_2 = sim_data[['Iteration', f'{agent1} Action']]
emu_data_reduced_2 = emu_data[['Iteration', f'{agent1} Action']]

# Merge the data on iteration
merged_data_1 = pd.merge(sim_data_reduced_1, emu_data_reduced_1, on='Iteration', suffixes=('_sim', '_emu'))
merged_data_2 = pd.merge(sim_data_reduced_2, emu_data_reduced_2, on='Iteration', suffixes=('_sim', '_emu'))

# Create subplots
fig, axs = plt.subplots(2, 1, figsize=(14, 10))

# Plot dataset 1
axs[0].scatter(merged_data_1['Iteration'], merged_data_1[f'{agent} Action_sim'], label='Simulation', color='blue', alpha=0.6)
axs[0].scatter(merged_data_1['Iteration'], merged_data_1[f'{agent} Action_emu'], label='Emulation', color='red', alpha=0.6)
axs[0].set_xlabel('Iteration')
axs[0].set_ylabel(f'{agent} Action')
axs[0].set_title(f'Dataset 1: Simulation vs Emulation')
axs[0].legend()
axs[0].grid(True)

# Plot dataset 2
axs[1].scatter(merged_data_2['Iteration'], merged_data_2[f'{agent1} Action_sim'], label='Simulation', color='blue', alpha=0.6)
axs[1].scatter(merged_data_2['Iteration'], merged_data_2[f'{agent1} Action_emu'], label='Emulation', color='red', alpha=0.6)
axs[1].set_xlabel('Iteration')
axs[1].set_ylabel(f'{agent1} Action')
axs[1].set_title(f'Dataset 2: Simulation vs Emulation')
axs[1].legend()
axs[1].grid(True)

plt.tight_layout()
plt.show()

