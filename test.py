# -*- coding: utf-8 -*-
"""
Created on Wed Nov 25 17:25:50 2020

@author: world
"""
from uCRDTPeer import uCRDTPeer
from setutils import check_completion
from p2pnetwork.node import Node
import setcommands
import time

HOST = '127.0.0.1'
PORT_INIT = 8000
tracking = []
PEER_STATUS = [False, False]

obj1 = uCRDTPeer(HOST, PORT_INIT+1)
obj2 = uCRDTPeer(HOST, PORT_INIT+2)

tracking.append(obj1)
tracking.append(obj2)

obj1.start()
obj2.start()

print("tracking!! \n")
obj1.connect_with_node(HOST, PORT_INIT + 2)
obj2.connect_with_node(HOST, PORT_INIT + 1)
print("connected \n")

# obj2.update_initial_local_text([('1', 0.1), (' ', 0.325), ('2', 0.55), (' ', 0.775)])
#obj1.update_initial_local_text([('1', 0.1), (' ', 0.325), ('2', 0.55), (' ', 0.775)])


#obj1.update_reference_name("apple")
# obj2.update_reference_name("orange")

print("1 out", obj1.nodes_outbound)
print("1 in", obj1.nodes_inbound)

#obj1.local_insertion()
obj1.send_to_nodes({"command": setcommands.INSERT, "character": 'c', "value": 0.5, "nodeID": 1})
time.sleep(2)
print(obj1._localText)
print(obj2._localText)

print("completed")

for p in range(len(tracking)):
    tracking[p].display_final_string()
    tracking[p].shutdown = True
    tracking[p].stop()
    
print("last")

    