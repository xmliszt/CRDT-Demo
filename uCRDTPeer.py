# -*- coding: utf-8 -*-
"""
Created on Wed Nov 25 00:40:56 2020

@author: world
"""

from p2pnetwork.node import Node
import time
from threading import Thread
import setutils
import random
import setcommands
import copy
'''
Some housekeeping data structures:

Edits: (setcommands.INSERT/DELETE, character: char, ordered value: float, nodeID source: int)
Local history: (Edits: Edits (above), historyIndex: int, successState: boolean)
Local text: (character: char, ordered value: float, nodeID: int)
Local delete: follows structure of edit
'''

class uCRDTPeer(Node):

    def  __init__(self, host, port, nodeID):
        super(uCRDTPeer, self).__init__(host, port, None)
        self._nodeID = nodeID
        self._debug = False
        self._referenceName = ""
        self._tokenisedReferenceName = []
        self._allowedToDelete = False
        self._indicesToDelete = []
        self._localText = []
        self._localHistory = []
        self._deleteBuffer = []
        self._allPeers = []
        #self._receivedOperations = []
        self._connectedOutboundPeers = []
        self._connectedInboundPeers = []
        self._completed = False
        self._worker = Thread(target=self.)
        
    # def start_node(self):
    #     self._worker.start()
    #     if self._debug:
    #         print(f"Node {self._nodeID} has started \n")

    # builtin default
    # appends newly received remote operations into buffer for processing later
    def node_message(self, node, data):
        self._localText, self._localHistory, self._deleteBuffer = setutils.handle_new_edits(self._localText, data, self._localHistory, self._deleteBuffer)
        #self._receivedOperations = setutils.append_incoming_operations(self._receivedOperations, data)
        if self._debug:
            print(f"Node {self._nodeID} has received a new operation: {data} from {node._nodeID} \n")

    # builtin default
    # when this node connects with other node
    # appends new node to outbound connection for tracking
    def outbound_node_connected(self, node):
        self._connectedOutboundPeers = setutils.add_outbound_connection(self._connectedOutboundPeers, node._nodeID)
        if self._debug:
            print(f"Node {self._nodeID} has an outbound connection with {node._nodeID} \n")


    # builtin default
    # when this node is trying to close an outbound connection
    # removes the outbound peer from buffer for tracking
    def outbound_node_disconnected(self, node):
        self._connectedOutboundPeers, outcome = setutils.remove_outbound_connection(self._connectedOutboundPeers, node._nodeID)
        if self._debug:
            if outcome:
                print(f"Node {self._nodeID} has successfully closed an outbound connection to {node._nodeID} \n")
            else:
                print(f"Node {self._nodeID} is unable to close an outbound connection to {node._nodeID} as the connection does not exist \n")

    # builtin default
    # when this node receives an inbound connection with other node
    # appends new node to inbound connection for tracking
    def inbound_node_connected(self, node):
        self._connectedInboundPeers = setutils.add_inbound_connection(self._connectedInboundPeers, node._nodeID)
        if self._debug:
            print(f"Node {self._nodeID} has an inbound connection with {node._nodeID} \n")

    # builtin default
    # when this node is trying to close an inbound connection
    # removes the inbound peer from buffer for tracking
    def inbound_node_disconnected(self, node):
        self._connectedInboundPeers, outcome = setutils.remove_inbound_connection(self._connectedInboundPeers, node._nodeID)
        if self._debug:
            if outcome:
                print(f"Node {self._nodeID} has successfully closed an inbound connection with {node._nodeID} \n")
            else:
                print(f"Node {self._nodeID} is unable to close an inbound connection with {node._nodeID} as the connection does not exist \n")

    # checks with all its inbound peers to update its localtext, localhistory and deletebuffer
    def request_reconnection(self):
        tempLocalText = []
        tempLocalHistory = []
        tempDeleteBuffer = []
        for p in self._allPeers:
            receivedLocalText, receivedLocalHistory, receivedDeleteBuffer = p.handle_reconnection()
            if len(receivedLocalText) > len(tempLocalText):
                tempLocalText = receivedLocalText
                tempLocalHistory = receivedLocalHistory
                tempDeleteBuffer = receivedDeleteBuffer
        self._localText = tempLocalText
        self._localHistory = tempLocalHistory
        self._deleteBuffer = tempDeleteBuffer
    
    # sends out its localtext, localhistory and deletebuffer
    def handle_reconnection(self):
        return copy.deepcopy(self._localText), copy.deepcopy(self._localHistory), copy.deepcopy(self._deleteBuffer)
        
    # initial
    # gives the peer communication access to other peers
    def update_peers_list(self, peers):
        self._allPeers = peers
        if self._debug:
            print(f"Node {self._nodeID} has received the list of other peers \n")
        
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
            
            
    # final
    # displays and returns the final local string for this node
    def display_final_string(self):
        finalString = setutils.display_final_string(self._currentText)
        print(f"Node {self._nodeID} has the final string state of: {finalString} \n")
        return finalString
    
    # inserts the name as one block
    def local_insertion(self):
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
                    edit = (setcommands.INSERT, editCharacter, editValue, self._nodeID)
                    self._localText, self._localHistory = setutils.insert_operation(self._localText, edit, self._localHistory) # update local copy
                    time.sleep(round(random.uniform(0,5), 1))
                    self.send_to_nodes(self, edit) # broadcast to all connected nodes
        if self.__debug:
            print(f"Node {self._nodeID} has completed insertion. Local text state: {self._localText} \n")
            
    # if allowed to delete, remove the corresponding strings 
    # returns true if all the strings that is to be deleted has been removed, false if not
    def local_deletion(self):
        originalDeleteList = copy.deepcopy(self._indicesToDelete)
        while self._allowedToDelete and len(originalDeleteList) > 0:
            position = None
            deleteIndex = originalDeleteList.pop(0)
            nextIndex = deleteIndex + 1
            status = False # checks if the string exists
            for i in range(len(self._localText)):
                if self._localText[i][0] == str(deleteIndex):
                    position = i
                    break
                
            # string found and exists
            try:
                if self._localText[position+2][0] != str(nextIndex):
                    status = True # did not hit the next index or out of position
            except IndexError:
                status = False # last index and string does not exist
             
            # found string and not empty    
            if status:
                while self._localText[position+2][0] != str(nextIndex):
                    edit = (setcommands.DELETE, self._localText[position+2][0], self._localText[position+2][1], self._localText[position+2][2])
                    self._localText, self._localHistory = setutils.local_delete_operation(self._localText, edit, self._localHistory) # update local copy
                    time.sleep(round(random.uniform(0,5), 1))
                    self.send_to_nodes(self, edit) # broadcast to all connected nodes         
                self._indicesToDelete.remove(deleteIndex)
                if self._debug:
                    print(f"Node {self._nodeID} has successfully deleted name belonging to {str(deleteIndex)} \n")
                continue
            
            # string not found
            else:
                startRange = self._localText[position+1][1]
                try:
                    endRange = self._localText[position+2][1]
                except IndexError:
                    endRange = 1.0
                finally:
                    previouslyDeleted = False
                    for i in self._localHistory[::-1]:
                        if i[0][2] > startRange and i[0][2] < endRange:
                            previouslyDeleted = True
                            break
                    if previouslyDeleted: # has been deleted before
                        self._indicesToDelete.remove(deleteIndex)
                        if self._debug:
                            print(f"Node {self._nodeID} is unable delete string belonging to {str(deleteIndex)} as it has been previously deleted \n")
                        continue
                    else: # no prior deletes found -> string not added yet
                        if self._debug:
                            print(f"Node {self._nodeID} is unable delete string as it has not been inserted yet \n")
                        continue
        
        if not self._indicesToDelete:
            return True
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
                        
        '''
        local insert and delete both okay OKATY
        remote insert and delete and merge insert okay, delete check if exist else put into delete buffer and refresh check
        if there was previous successful same delete, drop it. if not store in delete buffer
        request and send history
        maintain connection list, on connect, check if same length history and delete buffer, take the larger one,
        '''
