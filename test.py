# -*- coding: utf-8 -*-
"""
Created on Wed Nov 25 17:25:50 2020

@author: world
"""
from CRDTPeer import CRDTPeer
from setutils import check_completion

HOST = '0.0.0.0'
PORT_INIT = 8000
tracking = []
PEER_STATUS = [False, False]

obj1 = CRDTPeer(HOST, PORT_INIT+1, 1)
obj2 = CRDTPeer(HOST, PORT_INIT+2, 2)

tracking.append(obj1)
tracking.append(obj2)

print("tracking!!", tracking)
obj1.connect_with_node(HOST, PORT_INIT + 2)
obj2.connect_with_node(HOST, PORT_INIT + 1)

obj2.update_current_text([('1', 0.1), (' ', 0.325), ('2', 0.55), (' ', 0.775)])
obj1.update_current_text([('1', 0.1), (' ', 0.325), ('2', 0.55), (' ', 0.775)])

print("1", obj1._currentText)

print("2", obj2._currentText)

obj1.update_reference_name("apple")
obj2.update_reference_name("orange")

obj1.start_node()

obj2.start_node()


while True:
    if check_completion(tracking,PEER_STATUS):
        break
    
print("completed")

for p in range(len(tracking)):
    tracking[p].display()
    tracking[p].shutdown = True
    tracking[p].stop()
    
print("last")

    