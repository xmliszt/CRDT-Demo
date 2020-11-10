from p2pnetwork.node import Node
import commands
import time
from threading import Thread
from utils import get_operations, merge_operations
import sys


class Peer(Node):
    def __init__(self, host, port):
        super(Peer, self).__init__(host, port, None)
        self.__counter = 0
        self.operations = []
        self.__shutdown = False
        self.__waiting_for_input = False
        self.__worker = Thread(target=self._main_loop)
        self.__updater = Thread(target=self._check_updates)
        self.__worker.start()
        print(f"Node : {host}:{port} started ")

    # when receiving commands from other peers
    def node_message(self, node, data):
        self.operations = merge_operations(self.operations, data)

    def _check_updates(self):
        while not self.shutdown:
            time.sleep(1)
            while len(self.operations) > 0:
                tmp = self.__counter
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
                print(
                    f"\nCounter value {round(tmp, 2):<3} -> {round(self.__counter, 2):<3} by {c}"
                )

    def _get_op_and_send(self):
        time.sleep(1)
        self.__waiting_for_input = True
        operations = get_operations()
        self.__waiting_for_input = False
        if len(operations) == 0:
            self.shutdown = True
            self.stop()
        else:
            for each_operation in operations:
                self.peer_send_operation(each_operation)

    def _main_loop(self):
        while True:
            time.sleep(0.5)
            ip_address = input(
                "Enter the IP address [host:port] of the peer you want to connect with, or <Enter> to complete: "
            )
            if ip_address == "":
                break
            try:
                host = ip_address.split(':')[0]
                port = ip_address.split(':')[1]
                if port != self.port:
                    self.connect_with_node(host, int(port))
                    print(f"Connect with peer: {host}:{port}")
                continue
            except Exception:
                print("Invalid IP address!")
                continue
        self.__updater.start()
        while True:
            if not self.__waiting_for_input:
                self._get_op_and_send()

    def peer_send_operation(self, operation):
        op = operation[0]
        val = operation[1]
        data = ""
        if op == 'i':
            data = f"Update >>> {commands.INCREMENT}{val}{commands.INCREMENT}"
        elif op == 'd':
            data = f"Update >>> {commands.DECREMENT}{val}{commands.DECREMENT}"
        elif op == 'm':
            data = f"Update >>> {commands.MULTIPLY}{val}{commands.MULTIPLY}"
        elif op == 'l':
            data = f"Update >>> {commands.DIVIDE}{val}{commands.DIVIDE}"
        self.operations = merge_operations(self.operations, data)
        self.send_to_nodes(data, exclude=self.nodes_inbound)

    def stop(self):
        """Stop this node and terminate all the connected nodes."""
        self.node_request_to_stop()
        self.terminate_flag.set()
        sys.exit()

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