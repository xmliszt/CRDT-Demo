from p2pnetwork.node import Node
import commands

class Peer (Node):

    def __init__(self, host, port):
        super(Peer, self).__init__(host, port, None)
        self.__counter = 0
        print(f"Node {self.id} started on {host}:{port}")

    def node_message(self, node, data):
        print(f"Node {self.host}:{self.port} receives message: " + str(data))
        if commands.INCREMENT in data:
            n = int(data.split(commands.INCREMENT)[1])
            self.__counter += n
        elif commands.DECREMENT in data:
            n = int(data.split(commands.DECREMENT)[1])
            self.__counter -= n

    @property
    def counter(self):
        return self.__counter

    @counter.setter
    def counter(self, val):
        self.__counter = val