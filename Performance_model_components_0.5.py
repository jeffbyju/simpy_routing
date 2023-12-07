# -*- coding: utf-8 -*-
"""
Created on Mon Mar  30 06:58:05 2023

@author: bijus
"""

import simpy
import numpy as np

#Token is a representation of the message that gets passed around the network
class Token:
    """A token to be passed through the Fifo."""
    def __init__(self, id):
        self.id = id


#Source generates a unique token at every "interarrival_time" -This can be used to control freq of operation
#Tokens generated are send out through Fifo_out
class Source:
    """Generates tokens and feeds them into the Fifo."""
    def __init__(self, env, Fifo_out, interarrival_time):
        self.env = env
        self.Fifo_out = Fifo_out
        self.interarrival_dist = interarrival_time
        self.token_id = 0
        env.process(self.run())

    def run(self):
        while True:
            token = Token(self.token_id)
            yield env.timeout(self.interarrival_dist)  # Generate a token every interarrival_dist
            yield self.Fifo_out.put(token)
            print(f"{env.now}: Generated token {token.id}")
            self.token_id += 1
            
#Sink is the termination of the network. It takes Fifo_in tokens waits for processing_time to discard it
#processing_time can be used to control frequency of operation
class Sink:
    """A stage in the Fifo that processes tokens."""
    def __init__(self, env, name, Fifo_in, processing_time):
        self.env = env
        self.name = name
        self.Fifo_in = Fifo_in
        self.processing_time_dist = processing_time 
        env.process(self.run())

    def run(self):
        while True:
            token = yield self.Fifo_in.get()
            print(f"{env.now}: {self.name} Sunk token {token.id}")
            yield env.timeout(self.processing_time_dist)  # Simulate processing time
             
            

#Stage takes its input from a Fifo_in waits for processing_time and pass it on to Fifo_out
#processing_time can be used to control frequency of operation
class Stage:
    """A stage in the Fifo that processes tokens."""
    def __init__(self, env, name, Fifo_in, Fifo_out, processing_time):
        self.env = env
        self.name = name
        self.Fifo_in = Fifo_in
        self.Fifo_out = Fifo_out
        self.processing_time_dist = processing_time
        env.process(self.run())

    def run(self):
        while True:
            token = yield self.Fifo_in.get()
            print(f"{env.now}: {self.name} received token {token.id}")
            yield env.timeout(self.processing_time_dist)  # Simulate processing time
            yield self.Fifo_out.put(token)
            

#Decoder is a compoenent that takes inputs from Fifo_in and directs to one of its N output Fifos 
#Decoder directs the output using the information provided in address_range which is used to create an address map
class Decoder:

    def __init__(self, env, name, address_range, Fifo_in, Fifos, processing_time):
        self.env = env
        self.name = name
        self.address_range = address_range
        self.Fifo_in = Fifo_in
        self.Fifos = Fifos
        self.processing_time_dist = processing_time
        self.num_decoder_output = len(Fifos)
        self.addr_step = int(np.floor((address_range[1]-address_range[0])/self.num_decoder_output))
        env.process(self.run())
    def run(self):
        while True:
            token = yield self.Fifo_in.get()
            decoder_id = int(np.floor(token.id/self.addr_step))
            print(f"{env.now}: Decoded token {token.id} for decoder {decoder_id}")
            yield env.timeout(self.processing_time_dist)  # Simulate processing time
            yield self.Fifos[decoder_id].put(token)
   


# A compoenent that takes N inputs and directs to its output using a set algorithm (Say round robin scheduling()
class Arbiter:
    def __init__(self, env, name,Fifos, Fifo_out, processing_time):
        self.env = env
        self.name = name
        self.Fifos = Fifos        
        self.Fifo_out = Fifo_out
        self.processing_time_dist = processing_time
        self.last_serviced_Fifo = 0
        self.num_arbiter= len(Fifos)
        env.process(self.run())
   
    def run(self):
        while True:
            for i in range(0, self.num_arbiter):
                #Check if any of the input FIFOs are having values in the order of priority
                
                if (len(self.Fifos[self.last_serviced_Fifo].items) == 0):
                   self.last_serviced_Fifo = (self.last_serviced_Fifo + 1) % self.num_arbiter
                   #print(f"{env.now}: arbitration did not find anything in this FIFO")
                else:
                   print(f"{env.now}: arbitration FIFO has data - getting it")
                   token = yield self.Fifos[self.last_serviced_Fifo].get()
                   self.last_serviced_Fifo = (self.last_serviced_Fifo + 1) % self.num_arbiter
                   print(f"{env.now}: Arbited token {token.id} for arbiter out {self.last_serviced_Fifo}")
                   yield self.Fifo_out.put(token)
                   break
            yield env.timeout(self.processing_time_dist)  # Simulate processing time
            
            
            

# Simulation parameters
INTER_ARRIVAL_DISTANCE = 1
PROCESSING_TIME =1
NUM_DECODER_OUTPUT = 6
NUM_ARBITER_INPUT = 6
SIMULATION_DURATION = 100
env = simpy.Environment()

# assign values to start_address and end_address for decoder
START_ADDRESS = 0
END_ADDRESS = SIMULATION_DURATION
# create a list with the two integers
address_range = [START_ADDRESS, END_ADDRESS]


"""  Main code that connects all the components"""
# Create Fifo stages
fifo_in = simpy.Store(env, capacity=2)
fifo_out = simpy.Store(env, capacity=1)
fifo_out1 = simpy.Store(env, capacity=1)
fifo_out2 = simpy.Store(env, capacity=1)
#create a fifo list for the decoder
fifos = [simpy.Store(env, capacity=1) for _ in range(NUM_DECODER_OUTPUT)]

# Start the source process
source = Source(env, fifo_in, INTER_ARRIVAL_DISTANCE)
stage = Stage(env, "Stage 1", fifo_in, fifo_out, PROCESSING_TIME*1)
stage = Stage(env, "Stage 2", fifo_out, fifo_out1, PROCESSING_TIME)
#feed output of fifo_out1 to multiple pipes via decoder
decoder = Decoder(env, "Decoder1", address_range, fifo_out1, fifos, PROCESSING_TIME)
#Feed output from multiple pipes to a single fifo using an arbiter
arbiter =  Arbiter(env, "Arbiter1", fifos, fifo_out2, PROCESSING_TIME)

sink = Sink(env, "Sink1", fifo_out2, PROCESSING_TIME)  

# Run the simulation for 100 time units
env.run(until=SIMULATION_DURATION)
