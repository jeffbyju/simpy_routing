# NoC Performance Modeling Infrastructure

## STEPS TO RUN THE SIMULATION

1) Modify various properties of the simulation by modifying the values of the constants in "/constants.py"
2) Modify the network topology as well as the routing tables in the files "/device_config.json" and "/router_config.json"
3) Run the simulation using the command "python3 simulation.py" or "python simulation.py"
4) View a visualization of the data flow trace by loading the file "/example2.json" in the website "chrome://tracing/" to check the number of packets generated which were received at the destination device.
