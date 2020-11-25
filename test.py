# -*- coding: utf-8 -*-
"""
Created on Wed Nov 25 17:25:50 2020

@author: world
"""
from uCRDTPeer import uCRDTPeer
from setutils import check_completion

HOST = '0.0.0.0'
PORT_INIT = 8000
tracking = []
PEER_STATUS = [False, False]

obj1 = uCRDTPeer(HOST, PORT_INIT+1, 1)
obj2 = uCRDTPeer(HOST, PORT_INIT+2, 2)

tracking.append(obj1)
tracking.append(obj2)

print("tracking!!", tracking)
obj1.connect_with_node(HOST, PORT_INIT + 2)
obj2.connect_with_node(HOST, PORT_INIT + 1)

obj2.update_initial_local_text([('1', 0.1), (' ', 0.325), ('2', 0.55), (' ', 0.775)])
obj1.update_initial_local_text([('1', 0.1), (' ', 0.325), ('2', 0.55), (' ', 0.775)])


obj1.update_reference_name("apple")
obj2.update_reference_name("orange")

print("1 out", obj1.nodes_outbound)
print("1 in", obj1.nodes_inbound)

obj1.local_insertion()
print(obj1._localText)
print(obj2._localText)

    
print("completed")

for p in range(len(tracking)):
    tracking[p].display_final_string()
    tracking[p].shutdown = True
    tracking[p].stop()
    
print("last")

    