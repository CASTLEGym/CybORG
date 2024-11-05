#!/bin/bash

#need to install git
doas apt-get install git

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



# Clone the required Git repository
git clone -b wrappers https://github.com/CASTLEGym/CybORG.git

conda env create -f CybORG/RAMPART_CybORG_EMU/CybORG/CybORG/cage-2-cardiff/PUNCH/environment.yml
