import os
import matplotlib.pyplot as plt
import networkx as nx
from networkx import connected_components
from pprint import pprint
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from html import escape

def format_dict_for_display(data, indent=0):
    # Helper function to add indentation
    def add_indent(s, num_spaces):
        return " " * num_spaces + s
    
    if isinstance(data, dict):
        formatted_lines = []
        for key, value in data.items():
            if key != 'success':
                formatted_value = format_dict_for_display(value, indent + 4)  # Increase indent for nested dicts
                formatted_lines.append(add_indent(f"{key}: {formatted_value}", indent))
        return "<br>"+"<br>".join(formatted_lines)
    elif isinstance(data, list):
        formatted_list = [format_dict_for_display(item) for item in data]  # Apply formatting to each list item
        return "<br>".join([add_indent(item, indent) for item in formatted_list])
    else:
        return add_indent(str(data), indent)


class NetworkVisualizer:
    def __init__(self, agent_game_states):
        self.agent_game_states = agent_game_states
        self.type_to_symbol = {
            'router': 'triangle-up',  # Triangle
            'server': 'square',       # Square
            'host': 'circle',         # Circle
            'op_host': 'diamond',
            'op_server': 'square'
        }
        self.seed = 3113794652
        self.save = None
        
    def set_game_state(self, agent_game_states):
        self.agent_game_states = agent_game_states

    def set_seed(self, seed):
        self.seed = seed
        
    def _get_node_type(self, node):
        type = ""
        if 'router' in node:
            type = 'router'
        elif 'Op' in node:
            if 'Host' in node:
                type = 'op_host'
            else:
                type = 'op_server'
        elif 'Server' in node:
            type = 'server' 
        else:
            type = 'host'
        return type

    def _convert_reward_format(self, rewards, ordered=False):
        """
        Convert a dictionary of rewards into an HTML formatted list.
    
        Args:
        rewards (dict): A dictionary containing reward metrics and values.
    
        Returns:
        str: An HTML string representing the rewards in list format.
        """
        if not rewards:
            return '<br>No rewards'
        return "".join([f'<br>&nbsp;&nbsp;&nbsp;• {metric}: {round(value,2)}' for metric, value in rewards.items()])


    def plot(self, save=True):
        self.save = save
        for num_steps in self.agent_game_states:
            for red_agent_name in self.agent_game_states[num_steps]:
                for episode in self.agent_game_states[num_steps][red_agent_name]:
                    for step, state in self.agent_game_states[num_steps][red_agent_name][episode].items():
                        for agent in state:
                            self._plot_state(num_steps, red_agent_name, episode, step, agent, state[agent])

    def _plot_state(self, num_steps, red_agent_name, episode, step, agent, state):
        
        link_diagram = state['link_diagram']
        compromised_hosts = state['compromised_hosts']
        node_colors = state['node_colors']
        node_borders = state['node_borders']
        action_info = state['action_info']
        host_map = state['host_map']
        sim_obs = state['obs']
        reward = self._convert_reward_format(state['reward'])
        accumulate_reward = self._convert_reward_format(state['accumulate_reward'])

        # 'link_diagram' is the NetworkX graph
        pos = nx.spring_layout(link_diagram, seed=self.seed)
        
        edge_x = []
        edge_y = []
        for edge in link_diagram.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

        # Create edge trace
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines')
            
        # Prepare hover text and symbols for each node
        hover_text = []
        node_symbols = []
        node_x = []    
        node_y = []     
        node_names = []

        for i, node in enumerate(link_diagram.nodes()):
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            # Determine the status ...
            compromised = 'Yes' if node in compromised_hosts else 'No'
            node_names.append(node)
            hover_text.append(f"Node: {node}<br>IP Address: {host_map[node]}<br>Compromised: {compromised}")
            # Determine the type of the node and assign the corresponding symbol
            node_type = self._get_node_type(node)  # Replace this with your method to get node type
            node_symbols.append(self.type_to_symbol.get(node_type, 'circle'))  # Default to 'circle'
        
        # Create node trace
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            hovertext=hover_text,
            text=node_names,
            marker=dict(showscale=False, 
                        colorscale='Viridis', 
                        color=node_colors, 
                        line=dict(
                            color=[border['color'] for border in node_borders],  # List of colors for each marker
                            width=[border['width'] for border in node_borders],  # List of widths for each marker
                        ),
                        size=10, 
                        symbol=node_symbols
                       ),
            textposition="top center",  # Position the text above the markers
            textfont=dict(
                family="sans serif",
                size=12,
                color="black")
        )        

        # Create layout: Main Structure
        layout=go.Layout(
                            title=f'<br>Total Number of Steps: {num_steps}\
                                    <br>Red Agent Name: {red_agent_name}\
                                    <br>Episode: {episode+1}\
                                    <br>Display <b>{agent}</b> Agent\
                                    <br><b>Step {step+1}</b>',
                            title_x=0.00,
                            title_y=1.00,
                            titlefont_size=10,
                            showlegend=False,
                            hovermode='closest',
                            margin=dict(b=15,l=0,r=200,t=80),
                            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                        )
        
        # Create annotations for agent actions, initially invisible
        vertical_padding = 0.05
        # for idx, action_info in enumerate(action_info):
        simulation_obs = dict(
            xref='paper', yref='paper',
            x=1.25, y= 0.2 - vertical_padding,  # Adjust these positions as needed
            text=f"""
                <br>🎯{agent} Action: {action_info['action']}
                <br>✅Success: {action_info['success']}
                <br>👀Observations: 
                <br>{format_dict_for_display(sim_obs)}
                <br>💰Reward: {reward}
                """,
            showarrow=False,
            visible=True,  
            align="left",  # Ensure text is aligned for both agents
            font=dict(
                size=7,
                family="Arial, sans-serif"  # Arial font, fallback to default sans-serif
                ),
            bgcolor="rgba(255,255,255,0.9)",  # Semi-transparent white background
            bordercolor="black",  # Black border color
            borderwidth=2  # Border width
            )
        
        # emulation_obs = dict(
        #     xref='paper', yref='paper',
        #     x=1.25, y= 0.2 - vertical_padding,  # Adjust these positions as needed
        #     text=f"""<br>🎯{agent} Action: {action_info['action']}
        #             <br>✅Success: {action_info['success']}
        #             <br>👀Observations:
        #             <br>{mininet_obs}                    
        #             <br>💰Reward: {reward}
        #         """,
        #     showarrow=False,
        #     visible=True,  
        #     align="left",  # Ensure text is aligned for both agents
        #     font=dict(
        #         size=7,
        #         family="Arial, sans-serif"  # Arial font, fallback to default sans-serif
        #         ),
        #     bgcolor="rgba(255,255,255,0.9)",  # Semi-transparent white background
        #     bordercolor="black",  # Black border color
        #     borderwidth=2  # Border width
        #     )
        
        # observations_annotations = [simulation_obs, emulation_obs]
        observations_annotations = [simulation_obs]
        
        # Prepare and plot the figure
        fig = go.Figure(data=[edge_trace, node_trace], layout=layout)
        self._setup_annotations_and_buttons(fig, observations_annotations)

        # Save and show the figure
        if self.save:
            self._save_figure(fig, red_agent_name, step)
            
        fig.show()

    def _setup_annotations_and_buttons(self, fig, annotations):
        # ... code to set up annotations and buttons ...
        # Add a button to toggle the visibility of observation annotations
        fig.update_layout(
            width=1000,
            annotations=[],  # Include the annotations by default, shown initially
            updatemenus=[
                dict(
                    buttons=[
                        dict(label="Show Observations",
                             method="relayout",
                             args=[{"annotations": [annotations[0]]}]),  # Assuming annotations[0] is for simulation
                        # dict(label="Show Emulation Observations",
                        #      method="relayout",
                        #      args=[{"annotations": [annotations[1]]}]),  # Assuming annotations[1] is for emulation
                        dict(label="Hide Observations",
                             method="relayout",
                             args=[{"annotations": []}]),  # This should hide all annotations
                    ],
                    direction="down",
                    # pad={"r": 20, "t": 20},
                    showactive=True,
                    x=0.5,
                    # xanchor="left",
                    y=1.25,
                    # yanchor="top",
                    bordercolor="#c7c7c7",
                    borderwidth=2,
                    # bgcolor="#ff7f0e",
                )
            ]
        )
        
    def _save_figure(self, fig, red_agent, step):
        image_folder = f"images/{red_agent}"
        if not os.path.exists(image_folder):
            os.makedirs(image_folder, exist_ok=True)
        fig.write_image(f"{image_folder}/step{step+1}.png")
        