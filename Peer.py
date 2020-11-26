import threading
from p2pnetwork.node import Node
import commands
import time
import threading
from utils import merge_operations


class Peer(Node):
    def __init__(self, host, port):
        super(Peer, self).__init__(host, port, None)
        self.__counter = 1
        self.operations = []
        self.__shutdown = False
        self.__worker = threading.Thread(target=self._check_operations_update)
        self.__worker.start()
        # print(f"Node : {host}:{port} started ")

    # when receiving commands from other peers
    def node_message(self, node, data):
        self.operations = merge_operations(self.operations, data)

    def _check_operations_update(self):
        while True:
            if self.shutdown:
                break
            time.sleep(1)
            while len(self.operations) > 0:
                # tmp = self.__counter
                c = self.operations.pop(0)
                if commands.INCREMENT in c:
                    n = int(c.split(commands.INCREMENT)[1])
                    self.__counter += n
                elif commands.DECREMENT in c:
                    n = int(c.split(commands.DECREMENT)[1])
                    self.__counter -= n
                elif commands.MULTIPLY in c:
                    n = int(c.split(commands.MULTIPLY)[1])
                    self.__counter *= n
                elif commands.DIVIDE in c:
                    n = int(c.split(commands.DIVIDE)[1])
                    self.__counter /= n
                # print(
                #     f"Peer : {self.host}:{self.port}\tCounter value {round(tmp, 2):<5} -> {round(self.__counter, 2):<5} by {c}"
                # )

    def stop(self):
        """Stop this node and terminate all the connected nodes."""
        self.shutdown = True
        time.sleep(0.5)
        self.__worker.join()
        self.node_request_to_stop()
        self.terminate_flag.set()

    @property
    def counter(self):
        return self.__counter

    @counter.setter
    def counter(self, val):
        self.__counter = val

    @property
    def shutdown(self):
        return self.__shutdown

    @shutdown.setter
    def shutdown(self, val):
        self.__shutdown = val