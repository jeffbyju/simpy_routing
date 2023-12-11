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
        self.device_fifos = {}
        self.router_fifos = {}
        self.processing_time = processing_time
        self.network_config = network_config
        self.logger = logger
        self.env.process(self.run())

    def __del__(self):
        print(f"removing router {self.id} {self.env.now}")

    def run(self):
        while True:
        
            try:
                #yield self.env.timeout(self.processing_time)
                for device_id,device_fifos in self.device_fifos.items():
                    if len(device_fifos['in'].items) > 0:
                        token = yield device_fifos['in'].get()
                        #yield self.env.timeout(self.processing_time)
                        print(f"received token with id {token.id}, source id {token.source_id} and destination id {token.dest_id} at router id {self.id} at time {self.env.now}")
                        if TRACE_ROUTER==True:
                          self.logger.log_event((self.env.now, f'Router: received token with id {token.id}, source id {token.source_id} and destination id {token.dest_id} at router id {self.id} at time {self.env.now}','B', token.id, 0) )
                          self.logger.log_event((self.env.now+.9, f'Router: received token with id {token.id}, source id {token.source_id} and destination id {token.dest_id} at router id {self.id} at time {self.env.now}','E', token.id, 0) )
                        if self.network_config.get_device_router_id(token.dest_id) == self.id:
                            if len(self.device_fifos[token.dest_id]['out'].items) < STORE_CAPACITY:
                                yield self.device_fifos[token.dest_id]['out'].put(token)
                                print(f"routed the token with id {token.id} to target device with id {token.dest_id} at router {self.id} at time {self.env.now}")
                                if TRACE_ROUTER==True:
                                    self.logger.log_event((self.env.now, f'routed the token with id {token.id} to target device with id {token.dest_id} at router {self.id} at time {self.env.now}','B', token.id, 0) )
                                    self.logger.log_event((self.env.now+.9, f'routed the token with id {token.id} to target device with id {token.dest_id} at router {self.id} at time {self.env.now}','E', token.id, 0) )
                                    
                            else:
                                if len(device_fifos['in'].items) == STORE_CAPACITY:
                                   print(f"******************Could not put back {token.id} to previous router at time {self.env.now} as we couldnt push it to next********") 
                                yield device_fifos['in'].put(token)
                                if TRACE_ROUTER==True:
                                  self.logger.log_event((self.env.now, f'Had to put back token {token.id} destined to Router {token.dest_id} at router {self.id} input at time {self.env.now}','B', token.id, 0) )
                                  self.logger.log_event((self.env.now+.9, f'Had to put back token {token.id} destined to Router {token.dest_id} at router {self.id} input at time {self.env.now}','E', token.id, 0) )

                        else:
                            if len(self.router_fifos[self.network_config.get_next_router_id(self.id,self.network_config.get_device_router_id(token.dest_id))]['out'].items) < STORE_CAPACITY:
                                yield self.router_fifos[self.network_config.get_next_router_id(self.id,self.network_config.get_device_router_id(token.dest_id))]['out'].put(token)
                                print(f"routed the token with id {token.id} to router {self.network_config.get_next_router_id(self.id,self.network_config.get_device_router_id(token.dest_id))} at router {self.id} at time {self.env.now}")
                                if TRACE_ROUTER==True:
                                    self.logger.log_event((self.env.now, f'routed the token with id {token.id} to router {self.network_config.get_next_router_id(self.id,self.network_config.get_device_router_id(token.dest_id))} at router {self.id} at time {self.env.now}','B', token.id, 0) )
                                    self.logger.log_event((self.env.now+0.9, f'routed the token with id {token.id} to router {self.network_config.get_next_router_id(self.id,self.network_config.get_device_router_id(token.dest_id))} at router {self.id} at time {self.env.now}','E', token.id, 0) )
                                    
                            else:
                                if len(device_fifos['in'].items) == STORE_CAPACITY:
                                   print(f"******************Could not put back {token.id} to previous router at time {self.env.now} as we couldnt push it to next********") 
                                yield device_fifos['in'].put(token)
                                if TRACE_ROUTER==True:
                                   self.logger.log_event((self.env.now, f'Had to put back token {token.id} destined to Router {token.dest_id} at router {self.id} input at time {self.env.now}','B', token.id, 0) )
                                   self.logger.log_event((self.env.now+.9, f'Had to put back token {token.id} destined to Router {token.dest_id} at router {self.id} input at time {self.env.now}','E', token.id, 0) )

                for router_id,router_fifos in self.router_fifos.items():
                    if len(router_fifos['in'].items) > 0:
                        token = yield router_fifos['in'].get()
                        print(f"received token with id {token.id}, source id {token.source_id} and destination id {token.dest_id} at router id {self.id} at time {self.env.now}")
                        if TRACE_ROUTER==True:
                            self.logger.log_event((self.env.now, f'Router: received token with id {token.id}, source id {token.source_id} and destination id {token.dest_id} at router id {self.id} at time {self.env.now}','B', token.id, 0) )
                            self.logger.log_event((self.env.now+.9, f'Router: received token with id {token.id}, source id {token.source_id} and destination id {token.dest_id} at router id {self.id} at time {self.env.now}','E', token.id, 0) )
                        if self.network_config.get_device_router_id(token.dest_id) == self.id:
                            if len(self.device_fifos[token.dest_id]['out'].items) < STORE_CAPACITY:
                                yield self.device_fifos[token.dest_id]['out'].put(token)
                                print(f"routed the token with id {token.id} to target device with id {token.dest_id} at router {self.id} at time {self.env.now}")
                                if TRACE_ROUTER==True:
                                    self.logger.log_event((self.env.now, f'routed the token with id {token.id} to target device with id {token.dest_id} at router {self.id} at time {self.env.now}','B', token.id, 0) )
                                    self.logger.log_event((self.env.now+.9, f'routed the token with id {token.id} to target device with id {token.dest_id} at router {self.id} at time {self.env.now}','E', token.id, 0) )
                                    
                            else:
                                if len(device_fifos['in'].items) == STORE_CAPACITY:
                                    print(f"******************Could not put back {token.id} to previous router at time {self.env.now} as we couldnt push it to next********") 
                                yield router_fifos['in'].put(token)

                                if TRACE_ROUTER==True:
                                   self.logger.log_event((self.env.now, f'Had to put back token {token.id} destined to Router {token.dest_id} at router {self.id} input at time {self.env.now}','B', token.id, 0) )
                                   self.logger.log_event((self.env.now+.9, f'Had to put back token {token.id} destined to Router {token.dest_id} at router {self.id} input at time {self.env.now}','E', token.id, 0) )
                        else:
                            if len(self.router_fifos[self.network_config.get_next_router_id(self.id,self.network_config.get_device_router_id(token.dest_id))]['out'].items) < STORE_CAPACITY:
                                yield self.router_fifos[self.network_config.get_next_router_id(self.id,self.network_config.get_device_router_id(token.dest_id))]['out'].put(token)
                                print(f"routed the token with id {token.id} to router {self.network_config.get_next_router_id(self.id,self.network_config.get_device_router_id(token.dest_id))} at router {self.id} at time {self.env.now}")
                                if TRACE_ROUTER==True:
                                    self.logger.log_event((self.env.now, f'routed the token with id {token.id} to router {self.network_config.get_next_router_id(self.id,self.network_config.get_device_router_id(token.dest_id))} at router {self.id} at time {self.env.now}','B', token.id, 0) )
                                    self.logger.log_event((self.env.now+.9, f'routed the token with id {token.id} to router {self.network_config.get_next_router_id(self.id,self.network_config.get_device_router_id(token.dest_id))} at router {self.id} at time {self.env.now}','E', token.id, 0) )
                                    

                            else:
                                if len(device_fifos['in'].items) == STORE_CAPACITY:
                                   print(f"******************Could not put back {token.id} to previous router at time {self.env.now} as we couldnt push it to next********") 
                                yield router_fifos['in'].put(token)
                                if TRACE_ROUTER==True:
                                   self.logger.log_event((self.env.now, f'Had to put back token {token.id} destined to Router {token.dest_id} at router {self.id} input at time {self.env.now}','B', token.id, 0) )
                                   self.logger.log_event((self.env.now+.9, f'Had to put back token {token.id} destined to Router {token.dest_id} at router {self.id} input at time {self.env.now}','E', token.id, 0) )
                            
                yield self.env.timeout(self.processing_time)
            except Exception as e:
                print("exception")
                print(e)
            print(f"processed stuff for router with id {self.id} at time {self.env.now}")

class Device:
    def __init__(self,env,device_id,processing_time,network_config,logger):
        self.env = env
        self.id = device_id
        self.fifos = None
        self.router_id = None
        self.processing_time = processing_time
        self.network_config = network_config
        self.logger = logger
        self.env.process(self.run())

    def __del__(self):
        print(f"removing device {self.id} {self.env.now}")

    def run(self):
        while True:
            try:
                if self.fifos:
                    
                    if len(self.fifos['in'].items) > 0:
                        token = yield self.fifos['in'].get()
                        yield self.env.timeout(self.processing_time)
                        print(f"received a token with token id {token.id} at device {self.id} from device {token.source_id} at time {self.env.now}")
                        self.logger.log_event((self.env.now, f'Device:received a token with token id {token.id} at device {self.id} from device {token.source_id} at time {self.env.now}','B', token.id, 0) )
                        self.logger.log_event((self.env.now+0.9, f'Device:received a token with token id {token.id} at device {self.id} from device {token.source_id} at time {self.env.now}','E', token.id, 0) )

                    other_connected_devices = [device for device in self.network_config.get_devices() if (device.id != self.id and device.router_id)]
                    if len(other_connected_devices) >= 1:
                        random.seed(234)
                        dest_device = random.choice(other_connected_devices)
                        token = Token(self.id,dest_device.id)
                        yield self.env.timeout(self.processing_time)
                        if len(self.fifos['out'].items) < STORE_CAPACITY:
                            yield self.fifos['out'].put(token)
                            print(f"sent a token with token id {token.id} from device {self.id} to dest device {dest_device.id} via starting router {self.router_id} at time {self.env.now}")
                            self.logger.log_event((self.env.now, f'Device: sent a token with token id {token.id} from device {self.id} to dest device {dest_device.id} via starting router {self.router_id} at time {self.env.now}','B', token.id, 0) )
                            self.logger.log_event((self.env.now+0.9, f'Device: sent a token with token id {token.id} from device {self.id} to dest device {dest_device.id} via starting router {self.router_id} at time {self.env.now}','E', token.id, 0) )

                yield self.env.timeout(self.processing_time)
                print(f"processed stuff for device with id {self.id} at time {self.env.now}")
            except Exception as e:
                print("exception ",e)