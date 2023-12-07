import simpy

class Token:
    token_count = 0
    def __init__(self,source_id,dest_id):
        self.id = Token.token_count
        self.source_id = source_id
        self.dest_id = dest_id
        Token.token_count += 1
