#!/bin/bash

#need to install git
sudo apt-get install git

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



