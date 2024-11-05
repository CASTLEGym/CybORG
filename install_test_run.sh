#!/bin/bash

# for punch additional install 
# sudo apt install libffi7

# Prompt user to enter the team name
read -p "Please run in specific conda env, enter the team name (OPTIONS: ['default','punch']): " team

# Clone the required Git repository
#git clone -b wrappers https://github.com/CASTLEGym/CybORG.git


if [ "$team" == "default" ]; then
  echo "Please activate test_env"
  conda install -y pytorch pytorch-cuda=11.8 -c pytorch -c nvidia
  pip install torch-geometric
  pip install Flask

elif [ "$team" == "punch" ]; then
  # create environment apriori 
  echo "Please activate punch_env"
fi


# Navigate to the directory
cd CybORG/RAMPART_CybORG_EMU/CybORG/


pip install openstackclient
pip install pyvelociraptor
conda install -c conda-forge grpcio -y
pip install zmq


pip install --use-pep517 -e .

if [ "$team" == "punch" ]; then
  pip install --upgrade prettytable
fi

cd CybORG/cage-2-cardiff

python integrated_game_coordinator.py -t cardiff

cd ../..
echo "Test finished with team cardiff.. "