# -*- coding: utf-8 -*-
"""
Created on Wed Nov 25 21:33:58 2020

@author: world
"""

import time
from datetime import datetime
from uCRDTPeer import uCRDTPeer
import random
from random import randint
from setutils import input_test_decision, check_completion
import copy

DEBUG_MODE = 1 # 1 to debug
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

if __name__ == "__main__":
    # To set up all the peers
    while True:
        
        numberOfPeers = input("Enter the number of peers in the P2P network: ")
        
        try:
            numberOfPeers = int(numberOfPeers)
        except ValueError:
            print("Integer!")
            continue 
        
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
        p = uCRDTPeer(HOST, PORT_INIT + i + 1, i+1)
        peers.append(p)
        p.start()
        PEER_STATUS.append(False)
        if DEBUG_MODE == 1:
            p.update_debug_mode(True)
            
    peers[0].connect_with_node(HOST, PORT_INIT + 2)
    peers[1].connect_with_node(HOST, PORT_INIT + 1)    
    peers[0].connect_with_node(HOST, PORT_INIT + 1)
    peers[1].connect_with_node(HOST, PORT_INIT + 2)

    # for i, p in enumerate(peers):
    #     for idx in range(numberOfPeers):
    #         if i != idx:
    #             p.connect_with_node(HOST, PORT_INIT + idx + 1)
                
    print(f"You have successfully set up {len(peers)} peers with id ranging from 1 to {numberOfPeers}")
    
    # get test decision
    while True:
        testDecision = input_test_decision(peers)
        if not testDecision:
            continue
        break
    
    originalString = testDecision[0]
    deletingIndices = testDecision[1]
    decision = testDecision[2]
    
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
        print("out", peers[p]._connectedOutboundPeers)
        print("in", peers[p]._connectedInboundPeers)
        peers[p].update_peers_list(peers)
        peers[p].update_reference_name(copy.deepcopy(NAMES[p]))
        peers[p].update_initial_local_text(copy.deepcopy(originalString))
        #peers[p].start()
            
    peers[0].local_insertion()
    for p in peers:
        print("local")
        print(p._localText)
        
    while True:
        time.sleep(1)
        if check_completion(peers, PEER_STATUS):
            break
    
    for p in range(len(peers)):
        peers[p].display_final_string()
        peers[p].shutdown = True
        peers[p].stop()