# KEEP

The objective of this repo is to present a minimal implementation of our `KEEP` RL agent. Please see the `evaluation.py` file for an example of how to load the KEEP agent, and wrap the default environment for graph representation.

## Note

This repo contains a `requirements.txt` file, however it is assumed the user has CybORG installed as a module already. Please be sure to do this either with

    conda develop /path/to/cage-challenge-2/CybORG

for conda, or

    echo /path/to/cage-challenge/CybORG > /path/to/venv/lib/python3.10/site-packages/CybORG.pth

for venv.

## `graph_wrapper.wrapper.py:InductiveGraphWrapper`
This class is the backbone of our agent. It facilitates the translation between the default CAGE environment and our augmented graph environment. It inherits from the `from CybORG.Agents.Wrappers.ChallengeWrapper` class, upon which most prior works built from. The `wrapper.step(a)` function will process the actions output by the agent, pass those updates to the envrionment parent class, then update its internal state to keep track of changes in the graph structure (maintained in `graph_wrapper.observation_graph.py`).

## `keep_agent.py`
This file holds the PyTorch models that take as input the current state, and outputs an action. The only function that matters for inference is `model.get_action(graph_wrapper_observation)`. Use the `load_agent` function in that file to initialize the pretrained agent using the weights stored in the `model_weights/inductive_agent.pt` file.