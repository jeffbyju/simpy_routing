import simpy
from payload import *
import json
import random
from constants import *

class Router:
    def __init__(self,env,router_id,neighbors,routing,processing_time,network_config):
        self.env = env
        self.id = router_id
        self.neighbors = neighbors
        self.routing = routing
        self.device_fifos = {}
        self.router_fifos = {}
        self.processing_time = processing_time
        self.network_config = network_config
        self.env.process(self.run())

    # def route(self,fifo):
    #     if len(fifo.items) > 0:
    #         token = yield fifo.get()
    #         print(f"received token with id {token.id}, source id {token.source_id} and destination id {token.dest_id} at router id {self.id} at time {self.env.now}")
    #         if self.network_config.get_device_router_id(token.dest_id) == self.id:
    #             yield self.device_fifos[token.dest_id]['out'].put(token)
    #             print(f"routed the token with id {token.id} to target device with id {token.dest_id} at router {self.id} at time {self.env.now}")
    #         else:
    #             yield self.router_fifos[self.network_config.get_next_router_id(self.id,self.get_device_router_id(token.dest_id))]['out'].put(token)
    #             print(f"routed the token with id {token.id} to router {self.network_config.get_next_router_id(self.id,self.get_device_router_id(token.dest_id))} at router {self.id} at time {self.env.now}")
    def __del__(self):
        print(f"removing router {self.id} {self.env.now}")

    def run(self):
        while True:
        
            try:
                for device_id,device_fifos in self.device_fifos.items():
                    # self.route(device_fifos['in'])
                    # print(f"first {self.id} {self.env.now}")
                    
                    if len(device_fifos['in'].items) > 0:
                        # print(f"second {self.id} {self.env.now}")
                        token = yield device_fifos['in'].get()
                        # print(f"third {self.id} {self.env.now}")
                        print(f"received token with id {token.id}, source id {token.source_id} and destination id {token.dest_id} at router id {self.id} at time {self.env.now}")
                        if self.network_config.get_device_router_id(token.dest_id) == self.id:
                            if len(self.device_fifos[token.dest_id]['out'].items) < STORE_CAPACITY:
                                yield self.device_fifos[token.dest_id]['out'].put(token)
                                print(f"routed the token with id {token.id} to target device with id {token.dest_id} at router {self.id} at time {self.env.now}")
                            else:
                                yield device_fifos['in'].put(token)
                        else:
                            if len(self.router_fifos[self.network_config.get_next_router_id(self.id,self.network_config.get_device_router_id(token.dest_id))]['out'].items) < STORE_CAPACITY:
                                yield self.router_fifos[self.network_config.get_next_router_id(self.id,self.network_config.get_device_router_id(token.dest_id))]['out'].put(token)
                                print(f"routed the token with id {token.id} to router {self.network_config.get_next_router_id(self.id,self.network_config.get_device_router_id(token.dest_id))} at router {self.id} at time {self.env.now}")
                            else:
                                yield device_fifos['in'].put(token)

                for router_id,router_fifos in self.router_fifos.items():
                    # self.route(router_fifos['in'])
                    if len(router_fifos['in'].items) > 0:
                        token = yield router_fifos['in'].get()
                        print(f"received token with id {token.id}, source id {token.source_id} and destination id {token.dest_id} at router id {self.id} at time {self.env.now}")
                        if self.network_config.get_device_router_id(token.dest_id) == self.id:
                            if len(self.device_fifos[token.dest_id]['out'].items) < STORE_CAPACITY:
                                yield self.device_fifos[token.dest_id]['out'].put(token)
                                print(f"routed the token with id {token.id} to target device with id {token.dest_id} at router {self.id} at time {self.env.now}")
                            else:
                                yield router_fifos['in'].put(token)
                        else:
                            if len(self.router_fifos[self.network_config.get_next_router_id(self.id,self.network_config.get_device_router_id(token.dest_id))]['out'].items) < STORE_CAPACITY:
                                yield self.router_fifos[self.network_config.get_next_router_id(self.id,self.network_config.get_device_router_id(token.dest_id))]['out'].put(token)
                                print(f"routed the token with id {token.id} to router {self.network_config.get_next_router_id(self.id,self.network_config.get_device_router_id(token.dest_id))} at router {self.id} at time {self.env.now}")
                            else:
                                yield router_fifos['in'].put(token)
                            
                yield self.env.timeout(self.processing_time)
            except Exception as e:
                print("exception")
                print(e)
            print(f"processed stuff for router with id {self.id} at time {self.env.now}")

class Device:
    def __init__(self,env,device_id,processing_time,network_config):
        self.env = env
        self.id = device_id
        self.fifos = None
        self.router_id = None
        self.processing_time = processing_time
        self.network_config = network_config
        self.env.process(self.run())

    def __del__(self):
        print(f"removing device {self.id} {self.env.now}")

    def run(self):
        while True:
            try:
                if self.fifos:
                    if len(self.fifos['in'].items) > 0:
                        token = yield self.fifos['in'].get()
                        print(f"received a token with token id {token.id} at device {self.id} from device {token.source_id} at time {self.env.now}")
                    
                    other_connected_devices = [device for device in self.network_config.get_devices() if (device.id != self.id and device.router_id)]
                    if len(other_connected_devices) >= 1:
                        dest_device = random.choice(other_connected_devices)
                        token = Token(self.id,dest_device.id)
                        if len(self.fifos['out'].items) < STORE_CAPACITY:
                            yield self.fifos['out'].put(token)
                            print(f"sent a token with token id {token.id} from device {self.id} to dest device {dest_device.id} via starting router {self.router_id} at time {self.env.now}")
                yield self.env.timeout(self.processing_time)
                print(f"processed stuff for device with id {self.id} at time {self.env.now}")
            except Exception as e:
                print("exception ",e)

class Logger:
    def __init__(self,env,network_config):
        self.env = env
        self.network_config = network_config
        self.env.process(self.run())

    def run(self):
        while True:
            with open("logs",'a') as f:
                print(f"time {self.env.now}",file=f)
                print("device fifos content",file=f)
                for fifo in self.network_config.fifos[:8]:
                    print(fifo.items,file=f)
                print("router fifos content",file=f)
                for fifo in self.network_config.fifos[8:]:
                    print(fifo.items,file=f)
                print("",file=f)
                
                yield self.env.timeout(2)