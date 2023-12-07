import json
from devices import *
from constants import *
from collections import deque

class NetworkConfig:
    def __init__(self,env):
        self.routers = {}
        self.devices = {}
        self.fifos = []
        self.env = env

        with open(DEVICE_CONFIG_FILENAME) as f:
            device_config_data = json.load(f)
            for d in device_config_data:
                device = Device(env,d["id"],PROCESSING_TIME,self)
                self.devices[device.id] = device

        with open(ROUTER_CONFIG_FILENAME) as f:
            router_config_data = json.load(f)
            for r in router_config_data:
                router = Router(env,r["id"],r["neighbors"],r["routing"],PROCESSING_TIME,self)
                self.routers[router.id] = router

        for d in device_config_data:
            if "router_id" in d:
                fifo_in = simpy.Store(env,capacity=STORE_CAPACITY)
                fifo_out = simpy.Store(env,capacity=STORE_CAPACITY)
                self.devices[d["id"]].router_id = d["router_id"]
                self.devices[d["id"]].fifos = {'in':fifo_in,'out':fifo_out}
                self.routers[d["router_id"]].device_fifos[d["id"]] = {'in':fifo_out,'out':fifo_in}
                self.fifos.append(fifo_in)
                self.fifos.append(fifo_out)
        if len(router_config_data) > 0:
            visited = set()
            queue = deque([self.routers[router_config_data[0]["id"]]])
            while queue:
                curr_router = queue.popleft()
                if curr_router.id in visited:
                    continue
                visited.add(curr_router.id)
                for n in curr_router.neighbors:
                    if n not in visited:
                        queue.append(self.routers[n])
                        fifo_in = simpy.Store(env,capacity=STORE_CAPACITY)
                        fifo_out = simpy.Store(env,capacity=STORE_CAPACITY)
                        self.routers[curr_router.id].router_fifos[n] = {'in':fifo_in,'out':fifo_out}
                        self.routers[n].router_fifos[curr_router.id] = {'in':fifo_out,'out':fifo_in}
                        self.fifos.append(fifo_in)
                        self.fifos.append(fifo_out)

    def __del__(self):
        print("deleting ",self.env.now)

    def get_next_router_id(self,source_router_id,dest_router_id):
        return self.routers[source_router_id].routing[dest_router_id]
    
    def get_device_router_id(self,device_id):
        return self.devices[device_id].router_id

    def get_routers(self):
        return list(self.routers.values())
    
    def get_devices(self):
        return list(self.devices.values())