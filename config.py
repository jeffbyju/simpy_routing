import json
from devices import *
from constants import *
from collections import deque
from port import *
from buffer import *
import simpy

class NetworkConfig:
    def __init__(self,env,logger):
        self.routers = {}
        self.devices = {}
        self.ports = []
        self.logger = logger
        self.env = env

        with open(DEVICE_CONFIG_FILENAME) as f:
            device_config_data = json.load(f)
            for d in device_config_data:
                device = Device(env,d["id"],PROCESSING_TIME,self,logger)
                self.devices[device.id] = device

        with open(ROUTER_CONFIG_FILENAME) as f:
            router_config_data = json.load(f)
            for r in router_config_data:
                router = Router(env,r["id"],r["neighbors"],r["routing"],PROCESSING_TIME,self,logger)
                self.routers[router.id] = router

        for d in device_config_data:
            if "router_id" in d:
                out_port = Port()
                in_port = Port()
                buffer1 = simpy.Store(env,capacity=5)
                buffer2 = simpy.Store(env,capacity=2)
                buffer3 = simpy.Store(env,capacity=5)
                buffer4 = simpy.Store(env,capacity=2)

                out_port.set_vc1(buffer1)
                out_port.set_vc2(buffer2)
                in_port.set_vc1(buffer3)
                in_port.set_vc2(buffer4)

                self.devices[d["id"]].router_id = d["router_id"]
                self.devices[d["id"]].port = out_port
                self.routers[d["router_id"]].device_ports[d["id"]] = in_port

                out_port_credit_stores = {
                    'vc1':simpy.Container(self.env, init=5, capacity=5),
                    'vc2':simpy.Container(self.env, init=2, capacity=2)
                }

                in_port_credit_stores = {
                    'vc1':simpy.Container(self.env,init=5,capacity=5),
                    'vc2':simpy.Container(self.env,init=2,capacity=2)
                }

                self.devices[d["id"]].out_credit_stores = out_port_credit_stores
                self.devices[d["id"]].in_credit_stores = in_port_credit_stores
                self.routers[d["router_id"]].out_device_credit_stores[d["id"]] = in_port_credit_stores
                self.routers[d["router_id"]].in_device_credit_stores[d["id"]] = out_port_credit_stores
                
                self.ports.append(out_port)
                self.ports.append(in_port)


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

                        out_port = Port()
                        in_port = Port()
                        buffer1 = simpy.Store(env,capacity=5)
                        buffer2 = simpy.Store(env,capacity=2)
                        buffer3 = simpy.Store(env,capacity=5)
                        buffer4 = simpy.Store(env,capacity=2)

                        out_port.set_vc1(buffer1)
                        out_port.set_vc2(buffer2)
                        in_port.set_vc1(buffer3)
                        in_port.set_vc2(buffer4)

                        out_port_credit_stores = {
                            'vc1':simpy.Container(self.env, init=5, capacity=5),
                            'vc2':simpy.Container(self.env, init=2, capacity=2)
                        }

                        in_port_credit_stores = {
                            'vc1':simpy.Container(self.env,init=5,capacity=5),
                            'vc2':simpy.Container(self.env,init=2,capacity=2)
                        }

                        self.routers[n].router_ports[curr_router.id] = out_port
                        self.routers[curr_router.id].router_ports[n] = in_port

                        self.routers[n].in_router_credit_stores[curr_router.id] = out_port_credit_stores
                        self.routers[n].out_router_credit_stores[curr_router.id] = in_port_credit_stores 
                        self.routers[curr_router.id].in_router_credit_stores[n] = in_port_credit_stores
                        self.routers[curr_router.id].out_router_credit_stores[n] = out_port_credit_stores
                        
                        self.ports.append(out_port)
                        self.ports.append(in_port)

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