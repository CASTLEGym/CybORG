#!/bin/bash

conda create --name PUNCH_SB python=3.10 -y
conda activate PUNCH_SB

cd ../..


pip install openstackclient
pip install pyvelociraptor
conda install -c conda-forge grpcio -y
pip install -e .

cd CybORG/cage-2-cardiff/PUNCH

pip install -r requirements.txt
cd ..
python game_coordinator.py -t punch



