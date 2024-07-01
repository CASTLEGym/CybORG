# To run the emulation : 

Create a new folder in defender node: 

 Download these two scripts in the folder: 
 1. install_conda.sh  : curl -o install_conda.sh https://raw.githubusercontent.com/CASTLEGym/CybORG/wrappers/install_conda.sh
 2. install_test_run.sh : curl -o install_test_run.sh https://raw.githubusercontent.com/CASTLEGym/CybORG/wrappers/install_test_run.sh
 
# Make it executable : 

 - chmod 755 install_conda.sh
 - chmod 755 install_test_run.sh
 
 # Run the test: 
 - ./install_conda.sh
 - ./install_test_run.sh
 
 
 # game coordinator setting: 
 - set parameters:
   - -e: experiment (default: sim, for emulation : emu) 
   - -s: steps (int, default: 4)
   - -u : openstack username 
   - -p : openstack password
   - -t : Blue team   (default: cardiff)
 
