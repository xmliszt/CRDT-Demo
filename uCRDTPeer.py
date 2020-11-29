# -*- coding: utf-8 -*-
"""
Created on Wed Nov 25 00:40:56 2020

@author: world
"""

from Node import Node
import time
import setutils
import random
import setcommands
import copy
import asyncio

'''
Some housekeeping data structures:

Edits: {"command": setcommands.INSERT/DELETE, "character": char, "value": float, "nodeID": int)
Local history: (Edits: Edits (above), historyIndex: int, successState: boolean)
Local text: (character: char, ordered value: float, nodeID: int)
Local delete: follows structure of edit
'''

class uCRDTPeer(Node):

    def  __init__(self, host, port):
        super(uCRDTPeer, self).__init__(host, port, None)
        self._nodeID = ""
        self.__shutdown = False
        self._debug = False
        self._referenceName = ""
        self._tokenisedReferenceName = []
        self._allowedToDelete = False
        self._indicesToDelete = []
        self._localText = []
        self._localHistory = [({"command": 0, "character": 0, "value": 0, "nodeID": 0}, 0, True)]
        self._deleteBuffer = []
        self._allPeers = []
        #self._receivedOperations = []
        self._connectedOutboundPeers = []
        self._connectedInboundPeers = []
        self._tripleStatus = [False, False, False]
        self._completed = False
        self._sleeping = False
        self._testDecision = '0'
        # self._worker = Thread(target=self.refresh)
        # self._worker.start()
        
    def refresh(self):
        self._tripleStatus[1] = self.local_deletion()
        self._tripleStatus[2] = self.refresh_delete_buffer()
        print(f"Node {self._nodeID} has triple status of {self._tripleStatus}")
        if all(x == True for x in self._tripleStatus):
            self._completed = True         
            
    # builtin default
    # appends newly received remote operations into buffer for processing later
    def node_message(self, node, data):
        if not self._sleeping:
            self._localText, self._localHistory, self._deleteBuffer = setutils.handle_new_edits(self._localText, data, self._localHistory, self._deleteBuffer)
            self.refresh()
            #self._receivedOperations = setutils.append_incoming_operations(self._receivedOperations, data)
            # if self._debug:
            #     print(f"Node {self._nodeID} has received a new operation: {data} from {node.id} \n")

    # builtin default
    # when this node connects with other node
    # appends new node to outbound connection for tracking
    def outbound_node_connected(self, node):
        self._connectedOutboundPeers = setutils.add_outbound_connection(self._connectedOutboundPeers, node.id)
        # if self._debug:
        #     print(f"Node {self._nodeID} has an outbound connection with {node.id} \n")


    # builtin default
    # when this node is trying to close an outbound connection
    # removes the outbound peer from buffer for tracking
    def outbound_node_disconnected(self, node):
        self._connectedOutboundPeers, outcome = setutils.remove_outbound_connection(self._connectedOutboundPeers, node._nodeID)
        # if self._debug:
        #     if outcome:
        #         print(f"Node {self._nodeID} has successfully closed an outbound connection to {node.id} \n")
        #     else:
        #         print(f"Node {self._nodeID} is unable to close an outbound connection to {node.id} as the connection does not exist \n")

    # builtin default
    # when this node receives an inbound connection with other node
    # appends new node to inbound connection for tracking
    def inbound_node_connected(self, node):
        self._connectedInboundPeers = setutils.add_inbound_connection(self._connectedInboundPeers, node.id)
        # if self._debug:
        #     print(f"Node {self._nodeID} has an inbound connection with {node.id} \n")

    # builtin default
    # when this node is trying to close an inbound connection
    # removes the inbound peer from buffer for tracking
    def inbound_node_disconnected(self, node):
        self._connectedInboundPeers, outcome = setutils.remove_inbound_connection(self._connectedInboundPeers, node._nodeID)
        # if self._debug:
        #     if outcome:
        #         print(f"Node {self._nodeID} has successfully closed an inbound connection with {node.id} \n")
        #     else:
        #         print(f"Node {self._nodeID} is unable to close an inbound connection with {node.id} as the connection does not exist \n")

    # checks with all its inbound peers to update its localtext, localhistory and deletebuffer
    def request_reconnection(self):
        tempLocalTextSize = -1
        index = -1
        for p in range(len(self._allPeers)):
            rLTS = self._allPeers[p].handle_reconnection_size()
            if rLTS > tempLocalTextSize:
                tempLocalTextSize = rLTS
                index = p
        self._localText, self._localHistory, self._deleteBuffer = self._allPeers[index].handle_reconnection_information()
    
    # sends out its localtext, localhistory and deletebuffer
    def handle_reconnection_information(self):
        return copy.deepcopy(self._localText), copy.deepcopy(self._localHistory), copy.deepcopy(self._deleteBuffer)
        
    # sends out the size of its localtext
    def handle_reconnection_size(self):
        return len(self._localText)
    
    # initial
    # assigns the node its local id
    def update_nodeID(self, nodeID):
        self._nodeID = nodeID
        # if self._debug:
        #     print(f"Node has been assigned the id of {self._nodeID}")
    
    # initial
    # gives the peer communication access to other peers
    def update_peers_list(self, peers):
        self._allPeers = peers
        # if self._debug:
        #     print(f"Node {self._nodeID} has received the list of other peers \n")
            
    # initial
    # updates the peer on the test condition
    def update_test_decision(self, testDecision):
        self._testDecision = testDecision
        # if self._debug:
        #     print(f"Node {self._nodeID} has been informed of the test decision of {self._testDecision}")
        
    # initial
    # states if debug mode is True or False
    def update_debug_mode(self, debugStatus):
        self._debug = debugStatus
        
    # initial
    # updates and tokenises the reference name
    def update_reference_name(self, referenceNameString):
        self._referenceName = referenceNameString
        self._tokenisedReferenceName = setutils.tokenise_reference_name(referenceNameString)
        if self._debug:
            print(f"Node {self._nodeID} has been assigned the name of {self._referenceName} \n")
            
    # initial
    # updates delete status and the delete list if any
    def update_delete_status(self, deleteStatus, deletingList):
        self._allowedToDelete = deleteStatus
        self._indicesToDelete = deletingList
        if self._debug:
            if self._allowedToDelete:
                print(f"Node {self._nodeID} is allowed to delete the strings of {self._indicesToDelete} \n")
            else:
                print(f"Node {self._nodeID} is not allowed to delete any strings \n")
    
    # initial
    # updates the local copy
    def update_initial_local_text(self, initialText):
        self._localText = initialText
        if self._debug:
            print(f"Node {self._nodeID} has been given the initial text of {self._localText} \n")
            
    # initial
    # updates the sleeping status of the node
    def update_sleeping_status(self, sleepingStatus):
        self._sleeping = sleepingStatus
        if self._sleeping:
            if self._debug:
                print(f"Node {self._nodeID} has been designated to disconnect!")
        else: 
            if self._debug:
                print(f"Node {self._nodeID} has is alive with local text state of {self._localText}")
            self.request_reconnection()
            if self._debug:
                print(f"Node {self._nodeID} has requested local text updates to {self._localText}")
            self.local_insertion()
            self.refresh()
                
    # final
    # displays and returns the final local string for this node
    def display_final_string(self):
        finalString = setutils.display_final_string(self._localText)
        print(f"Node {self._nodeID} has the final string state of: {finalString} \n")
        return finalString
    
    # inserts the name as one block
    def local_insertion(self):
        if not self._sleeping:
            while len(self._tokenisedReferenceName) > 0:
                index = None
                for i in range(len(self._localText)):
                   if self._localText[i][0] == str(self._nodeID):
                       index = i
                       break   
                try:
                    valueRange = self._localText[index+2][1] - self._localText[index+1][1]
                except IndexError:
                    valueRange = 1.0 - self._localText[index+1][1]
                finally:  
                    step = valueRange/(len(self._tokenisedReferenceName)+1)
                    length = len(self._tokenisedReferenceName)
                    for i in range(length):
                        editCharacter = self._tokenisedReferenceName.pop(0)
                        editValue = (i+1)*step + self._localText[index+1][1]
                        edit = {"command": setcommands.INSERT, "character": editCharacter, "value": editValue, "nodeID": self._nodeID}
                        self._localText, self._localHistory = setutils.insert_operation(self._localText, edit, self._localHistory) # update local copy
                        time.sleep(round(random.uniform(0,5)/100, 1))
                        self.send_to_nodes(edit, exclude=self.nodes_inbound) # broadcast to all connected nodes
            if self._debug:
                print(f"Node {self._nodeID} has completed insertion. Local text state: {self._localText} \n")
            self._tripleStatus[0]  = True
            if all(x == True for x in self._tripleStatus):
                self._completed = True    
            return True
        else:
            return False
            
    
    # if allowed to delete, remove the corresponding strings 
    # returns true if all the strings that is to be deleted has been removed, false if not
    def local_deletion(self):
        if not self._sleeping:
            originalDeleteList = copy.deepcopy(self._indicesToDelete)
            while self._allowedToDelete and len(originalDeleteList) > 0:
                position = None
                deleteIndex = originalDeleteList.pop(0)
                nextIndex = deleteIndex + 1
                status = -1 # checks if the string exists
                for i in range(len(self._localText)):
                    if self._localText[i][0] == str(deleteIndex):
                        position = i
                        break
                
                try:
                    if self._localText[position+2][0] != str(nextIndex):
                        status = 1 # string found, could be at the end
                    else:
                        status = 0 # string not found and not at the end
                except IndexError:
                    status = False # string not found and at the end
                 
                # found string and not empty    
                if status == 1:
                    try:
                        while self._localText[position+2][0] != str(nextIndex):
                            edit = {"command": setcommands.DELETE, "character": self._localText[position+2][0], "value": self._localText[position+2][1], "nodeID": self._localText[position+2][2]}
                            self._localText, self._localHistory = setutils.local_delete_operation(self._localText, edit, self._localHistory) # update local copy
                            time.sleep(round(random.uniform(0,5)/10, 1))                            
                            self.send_to_nodes(edit, exclude=self.nodes_inbound) # broadcast to all connected nodes  
                    except IndexError:
                        pass
                    finally:
                        self._indicesToDelete.remove(deleteIndex)
                        if self._debug:
                            print(f"Node {self._nodeID} has successfully deleted name belonging to {str(deleteIndex)} \n")
                    continue
                
                # string not found and not at the end
                else:
                    startRange = self._localText[position+1][1]
                    try:
                        endRange = self._localText[position+2][1]
                    except IndexError:
                        endRange = 1.0
                    finally:
                        previouslyDeleted = False
                        for i in self._localHistory[::-1]:
                            if i[0]["value"] > startRange and i[0]["value"] < endRange:
                                previouslyDeleted = True
                                break
                        if previouslyDeleted: # has been deleted before
                            self._indicesToDelete.remove(deleteIndex)
                            if self._debug:
                                print(f"Node {self._nodeID} is unable delete string belonging to {str(deleteIndex)} as it has been previously deleted \n")
                        else: # no prior deletes found -> string not added yet
                            if self._debug:
                                print(f"Node {self._nodeID} is unable delete string as it has not been inserted yet \n")
                    continue
            
            if not self._indicesToDelete:
                self._tripleStatus[1] = True
                if all(x == True for x in self._tripleStatus):
                    self._completed = True    
                return True
            else:
                return False
        else:
            return False
        
    # refreshes the delete buffer
    # returns true if delete buffer is empty, false if it is not
    def refresh_delete_buffer(self):
        originalDeleteBuffer = copy.deepcopy(self._deleteBuffer)
        while len(originalDeleteBuffer) > 0:
            deleteEdit = originalDeleteBuffer.pop(0)
            found = False
            for i in self._localText:
                if i[0] == deleteEdit[1] and i[1] == deleteEdit[2]:
                    found = True
                    break
            if found:
                self._localText, self._localHistory = setutils.local_delete_operation(self._localText, deleteEdit, self._localHistory)
                self._deleteBuffer.remove(deleteEdit)
                if self._debug:
                    print(f"Node {self._nodeID} has removed {deleteEdit} from its delete buffer \n")
                continue
            else: # either in history or not existed
                previouslyDeleted = False
                for i in self._localHistory[::-1]:
                    if i[0] == deleteEdit:
                        previouslyDeleted = True
                        break
                if previouslyDeleted:
                    self._deleteBuffer.remove(deleteEdit)
                    if self._debug:
                        print(f"Node {self._nodeID} has removed {deleteEdit} from its delete buffer \n")
                    continue
                else:
                    if self._debug:
                        print(f"Node {self._nodeID} is unable to remove {deleteEdit} from its delete buffer \n")
                    continue
        if not self._deleteBuffer:
            return True
        else:
            return False
        
    # stop node and terminate connections to all other nodes
    def stop(self):
        #self._worker.join()
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
                        