class Client:
    def __init__(self, conn, addr, name, balance):
        self.conn = conn
        self.addr = addr
        self.name = name
        self.balance = balance