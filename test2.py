import simpy

class Sender:
    def __init__(self, env, name, data,capacity_credits, delay):
        self.env = env
        self.name = name
        self.data = data
        self.delay = delay
        self.out_pipe = None
        self.credits = simpy.Container(env, init=capacity_credits, capacity=capacity_credits)

    def set_out_pipe(self, out_pipe):
        self.out_pipe = out_pipe
        self.env.process(self.run())

    def run(self):
        for i in self.data:
            yield self.env.timeout(self.delay)
            while self.credits.level <= 0:
                print(f'Credit not available for {self.name} at {self.env.now}')
                yield self.env.timeout(1)
            yield self.out_pipe.put(i)
            print(f'{self.name} sending with credit {self.credits.level} at {self.env.now}')
            self.credits.get(1)

class Receiver:
    def __init__(self, env):
        self.env = env
        self.in_pipe1 = simpy.Store(env)
        self.in_pipe2 = simpy.Store(env)
        self.credit_store1 = None
        self.credit_store2 = None
        self.env.process(self.run())

    def set_credit_store(self, credit_store1, credit_store2):
        self.credit_store1 = credit_store1
        self.credit_store2 = credit_store2

    def run(self):
        while True:
            if len(self.in_pipe1.items) > 0:
                msg = yield self.in_pipe1.get()
                print(f'Received message: {msg} at {self.env.now}')
                self.credit_store1.put(1)
            if len(self.in_pipe2.items) > 0:
                msg = yield self.in_pipe2.get()
                print(f'Received message: {msg} at {self.env.now}')
                self.credit_store2.put(1)
            yield self.env.timeout(4)

# Setup and start simulation
env = simpy.Environment()

sender1 = Sender(env, 'sender1', [1, 2, 3, 4, 5], capacity_credits=4, delay=1)
sender2 = Sender(env, 'sender2', [6, 7, 8, 9, 10],capacity_credits=1, delay=1)

receiver = Receiver(env)
receiver.set_credit_store(sender1.credits, sender2.credits)

sender1.set_out_pipe(receiver.in_pipe1)
sender2.set_out_pipe(receiver.in_pipe2)

env.run(until=40)