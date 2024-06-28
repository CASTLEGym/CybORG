#!/bin/bash

#Agent specific sand box creation
conda create --name KEEP_SB python=3.10 -y
conda activate KEEP_SB

cd ../..
pip install openstackclient
pip install pyvelociraptor
conda install -c conda-forge grpcio -y
pip install -e .



cd CybORG/cage-2-cardiff/KEEP

pip install -r requirements.txt
cd ..
python game_coordinator.py -t keep



