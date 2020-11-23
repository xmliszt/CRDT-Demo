# -*- coding: utf-8 -*-
"""
Created on Tue Nov 10 23:27:51 2020

@author: world
"""

from p2pnetwork.node import Node
import time
from threading import Thread
from setutils import append_operations_for_display

class OutputPeer(Node):
    
    # init and run the thread
    def __init__(self, host, port):
        super(OutputPeer, self).__init__(host, port, None)
        self.operations = [] # store currently received operation
        self.history = [] # store all operations previously posted
        self.__referenceText = []
        self.__currentText = []
        self.__shutdown = False
        self.__worker = Thread(target=self._on_receive_operations_update)
        self.__worker.start()
        print(f"Output Node : {host}:{port} started")
        
    # when receiving commands from peers - builtin
    def node_message(self, node, data):
        append_operations_for_display(self.operations, data)
        
    # when prompted, empty out operations log and display on screen
    def _on_receive_operations_update(self):
        while True:
            
            # if this node has shut down => entire process is terminated
            if self.shutdown:
                break
            
            while len(self.operations) > 0:
                c = self.operations.pop(0)
                # print it out
                print(c)
                # append it to the history log
                self.history = self.history.append(c)
                
    # store texts
        
    # stop node and terminate connections to all other nodes
    def stop(self):
        self.__worker.join()
        self.node_request_to_stop()
        self.terminate_flag.set()
           
    @property
    # get shutdown status
    def shutdown(self):
        return self.__shutdown

    @shutdown.setter
    # changes the shutdown status
    def shutdown(self, val):
        self.__shutdown = val
        

