from p2pnetwork.node import Node
import commands


class Peer(Node):
    def __init__(self, host, port):
        super(Peer, self).__init__(host, port, None)
        self.__counter = 0
        print(f"Node {self.id} started on {host}:{port}")

    def node_message(self, node, data):
        _temp_counter_i = 0
        _temp_counter_m = 0
        print(f"Node {self.host}:{self.port} receives message: " + str(data))
        if commands.INCREMENT in data:
            n = int(data.split(commands.INCREMENT)[1])
            _temp_counter_i = self.__counter + n
        elif commands.MULTIPLE in data:
            n = int(data.split(commands.MULTIPLE)[1])
            _temp_counter_m = self.__counter * n
        self.__counter = max(_temp_counter_i, _temp_counter_m)
        print("Counter Value: ", self.__counter)

    @property
    def counter(self):
        return self.__counter

    @counter.setter
    def counter(self, val):
        self.__counter = val