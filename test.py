import simpy
#import json

events = []

"""
#When we dont have json module use the function below - Eg:- while using pypy
def create_json_file(events,txt_file ):    
    txt_file.write("[")
    for line in events:
        txt_file.write("{")
        for k in line.keys():
            txt_file.write(" \"{}\":\"{}\",".format(k, line[k]) )
        #Erase extra "," after last item of each line
        #Get the current file handler location
        r=txt_file.tell()    
        #Move to the left by one position
        txt_file.seek(r-1)            
        txt_file.write("},\n")
    #Erase Extra "," after the last line
    r=txt_file.tell()
    txt_file.seek(r-3)        
    txt_file.write("]")
 """  
def dump_chrome_trace(events, f):
    trace = {"traceEvents": events}
    f.write("[")
    for i, event in enumerate(trace["traceEvents"]):
            if i != 0:
                f.write(",")
            #Chrome trace doesn't like single quote - replace it with double
            event_str = '{}\n'.format(str(event).replace("'", '"'))
            f.write(event_str)
    f.write("]")
   
   

   

def log_event(event_data):
    event = {"name": event_data[1],"cat": "PERF","ph": event_data[2], "pid": event_data[3], "tid": event_data[4], "ts": event_data[0]}
    events.append(event)
   
def fetch(env, pipeline):
    for i in range(10):
        yield env.timeout(1)
        log_event((env.now, f'fetches {i}th instruction','B', i, 0) )
        log_event((env.now+.9, f'fetches {i}th instruction','E', i, 0) )
        #trace_event = {"event": "Fetching instruction", "instruction": i, "cycle": env.now}
        pipeline.put(i)
        print("Fetching instruction %d at cycle %d" % (i, env.now))
    pipeline.put(None)



def decode(env, pipeline1,pipeline2):
    while True:
        instr = yield pipeline1.get()
        if instr is None:
            break
        yield env.timeout(1)
        log_event((env.now, f'decodes {instr}th instruction','B', instr, 0) )
        log_event((env.now+.9, f'decodes {instr}th instruction','E', instr, 0) )
        pipeline2.put(instr)
        print("Decoding instruction %d at cycle %d" % (instr, env.now))

def execute(env, pipeline):
    while True:
        instr = yield pipeline.get()
        if instr is None:
            break
        yield env.timeout(1)
        log_event((env.now, f'Executes  {instr}th instruction','B', instr, 0) )
        log_event((env.now+.9, f'Executes {instr}th instruction','E', instr, 0) )
        print("Executing instruction %d at cycle %d" % (instr, env.now))


env = simpy.Environment()
pipeline1 = simpy.Store(env, capacity=20)
pipeline2 = simpy.Store(env, capacity=1)
env.process(fetch(env, pipeline1))
env.process(decode(env, pipeline1, pipeline2))
env.process(execute(env, pipeline2))

env.run(70)



# Write events to a JSON file
#with open("microprocessor_events.json", "w") as outfile:
#   json.dump(events, outfile)

with open("example.json", "w") as txt_file:
    dump_chrome_trace(events,txt_file )