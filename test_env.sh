#!/bin/bash

# Download the Miniconda installer
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh



# Run the installer
bash ~/miniconda.sh -b -p $HOME/miniconda

# Initialize Conda
eval "$($HOME/miniconda/bin/conda shell.bash hook)"
conda init


rm -rf ~/miniconda.sh 
# Verify installation
conda --version



conda create --name test_env python=3.10 -y
conda activate test_env
conda install -y pytorch  pytorch-cuda=11.8 -c pytorch -c nvidia

#need to install git
sudo apt-get install git

git clone -b wrappers https://github.com/CASTLEGym/CybORG.git

cd CybORG/CybORG/

pip install openstackclient
pip install pyvelociraptor
conda install -c conda-forge grpcio -y
pip install -e .

cd CybORG/cage-2-cardiff
python integrated_game_coordinator.py 
