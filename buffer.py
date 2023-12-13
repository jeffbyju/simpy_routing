class Buffer:
    def __init__(self,capacity):
        self.capacity = capacity
        self.container = [None for _ in range(capacity)]
        self.read_idx = 0
        self.write_idx = 0
        self.num_items = 0
    
    def peek(self):
        return self.container[self.read_idx]

    def read(self):        
        result = self.container[self.read_idx]
        self.container[self.read_idx] = None
        self.read_idx = (self.read_idx+1)%self.capacity
        self.num_items -= 1
        return result
    
    def write(self,item):
        self.container[self.write_idx] = item
        self.write_idx = (self.write_idx+1)%self.capacity
        self.num_items += 1
    
    def get_num_items(self):
        return self.num_items