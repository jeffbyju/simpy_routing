import simpy
from config import *
from constants import *

env = simpy.Environment()

network_config = NetworkConfig(env)
logger = Logger(env,network_config)
print("duration ",SIMULATION_DURATION)
env.run(until=SIMULATION_DURATION)