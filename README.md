# To run the emulation : 

Create a new folder in defender node: 

 Download these two scripts in the folder: 
  - install_conda.sh : curl -o install_conda.sh https://raw.githubusercontent.com/CASTLEGym/CybORG/wrappers/install_conda.sh
  - install_test_run.sh : curl -o install_test_run.sh https://raw.githubusercontent.com/CASTLEGym/CybORG/wrappers/install_test_run.sh
 

# Make it executable : 
 - chmod 755 install_conda.sh
 - chmod 755 install_test_run.sh
  
  
  
 1. install_conda.sh  : This is one time running and need not to rerun it. It install git, conda and create a new test envrionment.  Then we need to start a new shell, since conda is not recognisable after the installation in the same shell. Either source it, or restart a new shell. We should see your shell with a (base) enviromnemnt. This step also create a conda, test_env need to be activated manually.  
 2. Activate the test_env : conda activate test_env 
 3. install_test_run.sh :  It download the source code and install dependencies and code required for simulation and emulation. It will run the test simulation run with default values. (default mode: simulation, number of steps: 4) 
 

 
# Run the scripts: 
 - ./install_conda.sh
 - ./install_test_run.sh


 
# Game coordinator setting: 
We currently using the integrated_game_coordinator.py python script, that is in cage-2-cardiff folder located in subdirectory (CybORG/RAMPART_CybORG_EMU/CybORG/CybORG/cage-2-cardiff/) relative to new flode. cd to the folder and run it by : python integrated_game_cordinator.py 
 
 We can set the paramters of the game_coordinator using following :
 - set parameters:
   - -e: experiment (default: sim, for emulation : emu) 
   - -s: steps (int, default: 4)
   - -u : openstack username 
   - -p : openstack password
   - -t : Blue team   (default: cardiff)
 
