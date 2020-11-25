# -*- coding: utf-8 -*-
"""
Created on Tue Nov 10 23:02:31 2020

@author: world
"""

import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from CRDTPeer import CRDTPeer
import random
from random import randint
from setutils import input_test_decision, check_completion
import setcommands
import copy

DEBUG_MODE = 0 # 1 to debug
HOST = '0.0.0.0'
PORT_INIT = 8000
DELAY = 1000 # Simulate internet delay between peers in ms
NAMES = ["James", "Mary", "John", "Patricia", "Robert", 
         "Linda", "Michael", "Barbara", "William", "Elizabeth",
         "David", "Jennifer", "Richard", "Maria", "Charles",
         "Susan", "Joseph", "Margeret", "Thomas", "Dorothy",
         "Christopher", "Lisa", "Daniel", "Nancy", "Paul",
         "Karen", "Mark", "Betty", "Donald", "Helen", 
         "George", "Sandra", "Kenneth", "Donna", "Steven",
         "Carol", "Edward", "Ruth", "Brian", "Sharon",
         "Ronald", "Michelle", "Anthony", "Laura", "Kevin",
         "Sarah", "Jason", "Kimberly", "Jeff", "Deborah"]
PEER_STATUS = []


def debug_log(msg):
    if DEBUG_MODE:
        print(f"[{datetime.now()}]: {msg}")
          
if __name__ == "__main__":
    # To set up all the peers
    while True:
        
        numberOfPeers = input("Enter the number of peers in the P2P network: ")
        
        try:
            numberOfPeers = int(numberOfPeers)
        except ValueError:
            # restart loop
            print("Integer!")
            continue 
        
        # integer accepted
        if numberOfPeers < 2:
            print("At least 2 peers!")
            continue
        elif numberOfPeers > 50:
            print("Limit to less than 50 peers for demo purposes!")
            continue
        
        break
        
    # number of peers accepted
    peers = [] # keep track of peers   
    
    for i in range(numberOfPeers):
        p = CRDTPeer(HOST, PORT_INIT + i + 1, i+1)
        peers.append(p)
        #p.start()
        PEER_STATUS.append(False)
    
    # # set up p2p connection
    # print("hello!!!", peers)
    for i in peers:
        for j in range(len(peers)):
            if i != peers[j]:
                i.connect_with_node(HOST, PORT_INIT + j + 1)
                
            
    print(f"You have successfully set up {len(peers)} peers with id ranging from 1 to {numberOfPeers}")
    
    # get test decision
    while True:
        testDecision = input_test_decision(peers)
        if not testDecision:
            continue
        break
    
    originalString = testDecision[0]
    deletingIndices = testDecision[1]
    
    if deletingIndices[0] != -1:
        nodesToHandleDeleting = [[], []]
        
        for i in range(len(deletingIndices)):
            index = random.randint(0,1)
            nodesToHandleDeleting[index].append(deletingIndices[i])
            
        # send out to node 1 and node the deletes
        peers[0].update_delete_status(True, nodesToHandleDeleting[0])
        print("1 indices to delete", nodesToHandleDeleting[0])
        peers[1].update_delete_status(True, nodesToHandleDeleting[1])
        print("2 indices to delete", nodesToHandleDeleting[1])

    
    # send out the initial messages
    for p in range(len(peers)):
        peers[p].update_reference_name(NAMES[p])
        peers[p].update_current_text(copy.deepcopy(originalString))
        peers[p].start_node()
        if DEBUG_MODE:
            peers[p].update_debug(True)
        
    while True:
        time.sleep(1)
        if check_completion(peers, PEER_STATUS):
            break
    
    for p in range(len(peers)):
        peers[p].display()
        peers[p].shutdown = True
        peers[p].stop()
    
    

        
    
        
    
    
