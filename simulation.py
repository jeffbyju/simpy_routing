import simpy
from config import *
from constants import *
from tracing import *

env = simpy.Environment()

logger = Logger()
network_config = NetworkConfig(env,logger)
# debugger = Debugger(env,network_config)

print("duration ",SIMULATION_DURATION)
env.run(until=SIMULATION_DURATION)

logger.dump_chrome_trace("example2.json")