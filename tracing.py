class Logger:
    def __init__(self):
        self.events = []

    def dump_chrome_trace(self, file_name):
        with open(file_name,'w') as f:
            trace = {"traceEvents": self.events}
            f.write("[")
            for i, event in enumerate(trace["traceEvents"]):
                    if i != 0:
                        f.write(",")
                    #Chrome trace doesn't like single quote - replace it with double
                    event_str = '{}\n'.format(str(event).replace("'", '"'))
                    f.write(event_str)
            f.write("]")

    def log_event(self,event_data):
        event = {"name": event_data[1],"cat": "PERF","ph": event_data[2], "pid": event_data[3], "tid": event_data[4], "ts": event_data[0]}
        self.events.append(event)

class Debugger:
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
