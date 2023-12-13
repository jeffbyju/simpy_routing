class Port:
    def __init__(self):
        self.vc1 = None
        self.vc2 = None
    
    def set_vc1(self,buffer):
        self.vc1 = buffer
    
    def set_vc2(self,buffer):
        self.vc2 = buffer