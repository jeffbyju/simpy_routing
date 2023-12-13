PROCESSING_TIME = 2
SIMULATION_DURATION = 200
INTERARRIVAL_DIST = 2
STORE_CAPACITY = 1
DEVICE_CONFIG_FILENAME = "device_config.json"
ROUTER_CONFIG_FILENAME = "router_config.json"
VIRTUAL_CHANNELS = ["vc1","vc2"]

def get_complementary_channel(channel):
    return list(set(VIRTUAL_CHANNELS)-set([channel]))[0]