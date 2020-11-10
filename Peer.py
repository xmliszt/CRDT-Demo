from p2pnetwork.node import Node


class Peer(Node):
    def __init__(self, host, port):
        super(Peer, self).__init__(host, port, None)
        self.__counter = 1
        print(f"Node {self.id} started on {host}:{port}")

    def node_message(self, node, data):
        print(f"Node {self.host}:{self.port} receives message: " + str(data))
        self.__counter = max(self.__counter, data)
        print("Counter Value: ", self.__counter)

    @property
    def counter(self):
        return self.__counter

    @counter.setter
    def counter(self, val):
        self.__counter = val