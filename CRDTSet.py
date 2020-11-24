# -*- coding: utf-8 -*-
"""
Created on Tue Nov 10 23:02:31 2020

@author: world
"""

import time
from CRDTPeer import CRDTPeer
import random
from setutils import input_test_decision, check_completion, add_final_string, check_convergence, peer_convergence_values
import matplotlib.pyplot as plt 

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
# PEER_STATUS = []
# PEER_FINAL_STRING = []
ALL_TIMINGS = []

'''
Hi! This code is for automatic test running purposes
This test will run for maxNumberOfPeers^3 times to generate the graph
3 to obtain the average values and even out the random delay
Please change the following variables:
    maxNumberOfPeers: explained above
    testOption: either '1' or '2', where 1 only has insert operation, 2 has insert and random delete operation
    deleteInput: integer ranging from 0 to maxNumberOfPeers, only useful when testOption = '2'
'''
maxNumberOfPeers = 3 # don't exceed 50
testOption = '2'
deleteInput = 2
          
if __name__ == "__main__":
        
    for peersInNetwork in range(2,maxNumberOfPeers + 1):
        
        timing = []
        for attempts in range(3):
            
            start = time.perf_counter()
            PEER_STATUS = []
            PEER_FINAL_STRING = []
            
            while True:
                
                # numberOfPeers = input("Enter the number of peers in the P2P network: ")
                numberOfPeers = peersInNetwork
                
                try:
                    numberOfPeers = int(numberOfPeers)
                except ValueError:
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
                p.start()
                PEER_STATUS.append(False)
            
            # set up p2p connection
            for i, p in enumerate(peers):
                for idx in range(numberOfPeers):
                    if i != idx:
                        p.connect_with_node(HOST, PORT_INIT + idx + 1)
                    
            print(f"You have successfully set up {len(peers)} peers with id ranging from 1 to {numberOfPeers}")
            
            # get test decision
            while True:
                testDecision = input_test_decision(peers, testOption, str(deleteInput))
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
                    
                # send out to node 1 and node 2 the deletes
                peers[0].update_delete_status(True, nodesToHandleDeleting[0])
                print("1 indices to delete", nodesToHandleDeleting[0])
                peers[1].update_delete_status(True, nodesToHandleDeleting[1])
                print("2 indices to delete", nodesToHandleDeleting[1])
        
            
            # send out the initial messages
            for p in range(len(peers)):
                peers[p].update_reference_name(NAMES[p])
                peers[p].update_current_text(originalString)
                peers[p].start_node()
                if DEBUG_MODE:
                    peers[p].update_debug(True)
                
            while True:
                time.sleep(1)
                if check_completion(peers, PEER_STATUS):
                    break
            
            for p in range(len(peers)):
                string = peers[p].display()
                PEER_FINAL_STRING = add_final_string(PEER_FINAL_STRING, string)
                peers[p].shutdown = True
                peers[p].stop()
                
            convergence = check_convergence(PEER_FINAL_STRING)
            print("Checking convergence of all nodes:", convergence)
        
            end = time.perf_counter()
            duration = end - start
            timing.append(duration)
            time.sleep(10) # make sure the nodes end properly
        
        ALL_TIMINGS.append(timing)
        
    print("done!")
    xValues, yValues = peer_convergence_values(ALL_TIMINGS)
    plt.plot(xValues, yValues)
    plt.xlabel("number of peers")
    plt.ylabel("timing for convergence")
    plt.show()
         
    

        
    
        
    
    
