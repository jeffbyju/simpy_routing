# NoC Performance Modeling Infrastructure

## STEPS TO RUN THE SIMULATION

1) Modify various properties of the simulation by modifying the values of the constants in "/constants.py"
2) Modify the network topology as well as the routing tables in the files "/device_config.json" and "/router_config.json"
3) Run the simulation using the command "python3 simulation.py" or "python simulation.py" in the root project directory.
4) View a visualization of the data flow trace by loading the file "/example2.json" in the website "chrome://tracing/" to check the number of packets generated which were received at the destination device. Each row in the visualization corresponds to a single packet having either 1 or 2 vertical lines. The appearance of two lines indicates that the packet was successfuly routed to the destination device. The appearance of a single line indicates that the packet couldn't be routed to the destination device before the simulation ended.
