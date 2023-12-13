import simpy
from payload import *
import json
import random
from constants import *
from tracing import *

class Router:
    def __init__(self,env,router_id,neighbors,routing,processing_time,network_config,logger):
        self.env = env
        self.id = router_id
        self.neighbors = neighbors
        self.routing = routing
        self.device_ports = {}
        self.router_ports = {}
        self.router_credit_stores = {}
        self.device_credit_stores = {}
        self.processing_time = processing_time
        self.network_config = network_config
        self.logger = logger
        self.env.process(self.run())

    def __del__(self):
        print(f"removing router {self.id} {self.env.now}")

    def run(self):
        while True:
        
            try:
                for device_id,device_ports in self.device_ports.items():
                    for channel in VIRTUAL_CHANNELS:
                        buffer = getattr(device_ports,channel)

                        if len(buffer.items) > 0:
                            token = buffer.items[0]
                            print(f"received token with id {token.id}, source id {token.source_id} and destination id {token.dest_id} at router id {self.id} at time {self.env.now} ",token)
                            if self.network_config.get_device_router_id(token.dest_id) == self.id:
                                print("entered 1")
                                if self.device_credit_stores[token.dest_id][channel].level == 0:
                                    complementary_channel = get_complementary_channel(channel)
                                    print(f"entering complementary channel {complementary_channel} for device {device_id} at router {self.id}")
                                    if self.device_credit_stores[token.dest_id][complementary_channel].level > 0:
                                        print("before ",buffer.items)
                                        yield buffer.get()
                                        print("after ",buffer.items)
                                        yield self.device_credit_stores[token.dest_id][complementary_channel].get(1)
                                        yield self.device_credit_stores[device_id][channel].put(1)
                                        getattr(self.device_ports[token.dest_id],complementary_channel).write(token)
                                        print(f"routed the token with id {token.id} to target device with id {token.dest_id} at router {self.id} at time {self.env.now}")
                                    else:
                                        print(f"credit not available for device port {device_id} channel {channel} at router {self.id}")
                                else:
                                    print(f"entering channel {channel} for device {device_id} at router {self.id}")
                                    print("before ",buffer.items)
                                    yield buffer.get()
                                    print("after ",buffer.items)
                                    yield self.device_credit_stores[token.dest_id][channel].get(1)
                                    yield self.device_credit_stores[device_id][channel].put(1)
                                    getattr(self.device_ports[token.dest_id],channel).write(token)
                                    print(f"routed the token with id {token.id} to target device with id {token.dest_id} at router {self.id} at time {self.env.now}")
                            else:
                                print("entered 4")
                                next_router_id = self.network_config.get_next_router_id(self.id,self.network_config.get_device_router_id(token.dest_id))
                                if self.router_credit_stores[next_router_id][channel].level == 0:
                                    complementary_channel = get_complementary_channel(channel)
                                    if self.router_credit_stores[next_router_id][complementary_channel].level > 0:
                                        print("before ",buffer.items)
                                        yield buffer.get()
                                        print("after ",buffer.items)
                                        yield self.router_credit_stores[next_router_id][complementary_channel].get(1)
                                        yield self.device_credit_stores[device_id][channel].put(1)
                                        getattr(self.router_ports[next_router_id],complementary_channel).write(token)
                                        print(f"routed the token with id {token.id} to router {self.network_config.get_next_router_id(self.id,self.network_config.get_device_router_id(token.dest_id))} at router {self.id} at time {self.env.now}")
                                else:
                                    print("before ",buffer.items)
                                    yield buffer.get()
                                    print("after ",buffer.items)
                                    yield self.router_credit_stores[next_router_id][channel].get(1)
                                    print("yo")
                                    yield self.device_credit_stores[device_id][channel].put(1)
                                    print("yo2")
                                    getattr(self.router_ports[next_router_id],channel).write(token)
                                    print(f"routed the token with id {token.id} to router {self.network_config.get_next_router_id(self.id,self.network_config.get_device_router_id(token.dest_id))} at router {self.id} at time {self.env.now}")

                for router_id,router_ports in self.router_ports.items():
                    for channel in VIRTUAL_CHANNELS:
                        buffer = getattr(router_ports,channel)

                        if len(buffer.items) > 0:            
                            token = buffer.items[0]
                            print(f"received token with id {token.id}, source id {token.source_id} and destination id {token.dest_id} at router id {self.id} at time {self.env.now} ",token)
                            if self.network_config.get_device_router_id(token.dest_id) == self.id:
                                print("entered 2")
                                if self.device_credit_stores[token.dest_id][channel].level == 0:
                                    complementary_channel = get_complementary_channel(channel)
                                    print("entered 10")
                                    if self.device_credit_stores[token.dest_id][complementary_channel].level > 0:
                                        print("entered 11")
                                        yield buffer.get()
                                        yield self.device_credit_stores[token.dest_id][complementary_channel].get(1)
                                        yield self.router_credit_stores[router_id][channel].put(1)
                                        getattr(self.device_ports[token.dest_id],complementary_channel).write(token)
                                        print(f"routed the token with id {token.id} to target device with id {token.dest_id} at router {self.id} at time {self.env.now}")
                                else:
                                    yield buffer.get()
                                    yield self.device_credit_stores[token.dest_id][channel].get(1)
                                    yield self.router_credit_stores[router_id][channel].put(1)
                                    getattr(self.device_ports[token.dest_id],channel).write(token)
                                    print(f"routed the token with id {token.id} to target device with id {token.dest_id} at router {self.id} at time {self.env.now}")
                            else:
                                print("entered 3")
                                next_router_id = self.network_config.get_next_router_id(self.id,self.network_config.get_device_router_id(token.dest_id))
                                if self.router_credit_stores[next_router_id][channel].level == 0:
                                    complementary_channel = get_complementary_channel(channel)
                                    print("entered 12")
                                    if self.router_credit_stores[next_router_id][complementary_channel].level > 0:
                                        print("entered 13")
                                        yield buffer.get()
                                        yield self.router_credit_stores[next_router_id][complementary_channel].get(1)
                                        yield self.router_credit_stores[router_id][channel].put(1)
                                        getattr(self.router_ports[next_router_id],complementary_channel).write(token)
                                        print(f"routed the token with id {token.id} to router {self.network_config.get_next_router_id(self.id,self.network_config.get_device_router_id(token.dest_id))} at router {self.id} at time {self.env.now}")
                                else:
                                    yield buffer.get()
                                    yield self.router_credit_stores[next_router_id][channel].get(1)
                                    yield self.router_credit_stores[router_id][channel].put(1)
                                    getattr(self.router_ports[next_router_id],channel).write(token)
                                    print(f"routed the token with id {token.id} to router {self.network_config.get_next_router_id(self.id,self.network_config.get_device_router_id(token.dest_id))} at router {self.id} at time {self.env.now}")
                        
                yield self.env.timeout(self.processing_time)
            except Exception as e:
                print("exception")
                print(e)
            print(f"processed stuff for router with id {self.id} at time {self.env.now}")

class Device:
    def __init__(self,env,device_id,processing_time,network_config,logger):
        self.env = env
        self.id = device_id
        self.port = None
        self.router_id = None
        self.router_credit_stores = None
        self.processing_time = processing_time
        self.network_config = network_config
        self.logger = logger
        self.env.process(self.run())

    def __del__(self):
        print(f"removing device {self.id} {self.env.now}")

    def run(self):
        while True:
            try:
                if self.router_id:
                    for channel in VIRTUAL_CHANNELS:
                        buffer = getattr(self.port,channel)
                        
                        if len(buffer.items) > 0:
                            token = buffer.items[0]
                            yield buffer.get()
                            yield self.network_config.routers[self.router_id].device_credit_stores[self.id].put(1)
                            
                            print(f"received a token with token id {token.id} at device {self.id} from device {token.source_id} at time {self.env.now}")
                            self.logger.log_event((self.env.now, f'received a token with token id {token.id} at device {self.id} from device {token.source_id} at time {self.env.now}','B', token.id, 0) )
                            self.logger.log_event((self.env.now+0.9, f'received a token with token id {token.id} at device {self.id} from device {token.source_id} at time {self.env.now}','E', token.id, 0) )

                    other_connected_devices = [device for device in self.network_config.get_devices() if (device.id != self.id and device.router_id)]
                    if len(other_connected_devices) >= 1:
                        # random.seed(234)
                        dest_device = random.choice(other_connected_devices)
                        token = Token(self.id,dest_device.id)
                        chosen_channel = random.choice(VIRTUAL_CHANNELS)

                        while self.router_credit_stores[chosen_channel].level <= 0:
                            print(f'Credit not available for router {self.router_id} at {self.env.now}')
                            yield self.env.timeout(1)

                        yield self.router_credit_stores[chosen_channel].get(1)
                        getattr(self.network_config.routers[self.router_id].device_ports[self.id],chosen_channel).write(token)

                        print(f"sent a token with token id {token.id} from device {self.id} to dest device {dest_device.id} via starting router {self.router_id} at time {self.env.now}")
                        self.logger.log_event((self.env.now, f'sent a token with token id {token.id} from device {self.id} to dest device {dest_device.id} via starting router {self.router_id} at time {self.env.now}','B', token.id, 0) )
                        self.logger.log_event((self.env.now+0.9, f'sent a token with token id {token.id} from device {self.id} to dest device {dest_device.id} via starting router {self.router_id} at time {self.env.now}','E', token.id, 0) )

                yield self.env.timeout(self.processing_time)
                print(f"processed stuff for device with id {self.id} at time {self.env.now}")
                self.logger.dump_chrome_trace("example2.json")
            except Exception as e:
                print("exception ",e)