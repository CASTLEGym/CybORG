#!/bin/bash


conda install -y pytorch  pytorch-cuda=11.8 -c pytorch -c nvidia



git clone -b wrappers https://github.com/CASTLEGym/CybORG.git

cd CybORG/RAMPART_CybORG_EMU/CybORG/

pip install openstackclient
pip install pyvelociraptor
conda install -c conda-forge grpcio -y
pip install zmq
pip install -e .

cd CybORG/cage-2-cardiff
python integrated_game_coordinator.py 
