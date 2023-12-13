import simpy

class Port:
    def __init__(self, env, virtual_channel_credits):
        self.env = env
        self.store = simpy.Store(env)
        self.virtual_channels = virtual_channel_credits
        self.buffer = {vc: [] for vc in virtual_channel_credits}

    def getPort(self, vc):
        if len(self.store.items) > 0 and len(self.buffer[vc]) < self.virtual_channels[vc]:
            msg = yield self.store.get()
            self.buffer[vc].append(msg)
            return msg
        return "failure"

    def putPort(self, token, vc):
        if self.virtual_channels[vc] > len(self.buffer[vc]):
            yield self.store.put(token)
            return "success"
        return "failure"