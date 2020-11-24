# -*- coding: utf-8 -*-
"""
Created on Sat Nov 21 14:32:49 2020

@author: world
"""

from p2pnetwork.node import Node
import time
from threading import Thread
from setutils import append_operations_for_edits, handle_new_edits, tokenise_reference_name, insert_operation, delete_operation, display_final_string
import random
import setcommands


class CRDTPeer(Node):

    def __init__(self, host, port, nodeID):
        super(CRDTPeer, self).__init__(host, port, None)
        self.__currentText = []
        self.__tokenisedReferenceName = []
        self.__referenceName = ""
        self.__deletingIndices = [] # indices to delete
        self.__allowedToDelete = False
        self.__nodeID = nodeID
        self.receivedOperations = []
        self.__history = [((0, 0, 0, 0), 0, True)]
        self.completed = False
        self.__shutdown = False
        self.__debug = False
        self.__worker = Thread(target=self._check_operation_update)


    # when receiving messges from other nodes - builtin, check delete mode
    def node_message(self, node, data):
        self.receivedOperations = append_operations_for_edits(self.receivedOperations, data)
        
    # initial update
    def update_debug(self, debug):
        self.__debug = debug
    
    #initial update
    def start_node(self):
        self.__worker.start()
        if self.__debug:
            print(f"Node {self.__nodeID} started")

    # initial update
    def update_reference_name(self, referenceNameString):
        self.__referenceName = referenceNameString
        self.__tokenisedReferenceName = tokenise_reference_name(referenceNameString)
        print(f"Node {self.__nodeID} has the name of {self.__referenceName}")

    def update_current_text(self, currentText):
        self.__currentText = currentText

    # initial update
    def update_delete_status(self, deleteStatus, deletingList):
        self.__allowedToDelete = deleteStatus
        self.__deletingIndices = deletingList
        
    def display(self):
        finalString = display_final_string(self.__currentText)
        print(f"final {self.__nodeID} with {finalString} \n")
        return finalString

    def _check_operation_update(self):
        while True:

            time.sleep(round(random.uniform(0,3), 1)/10)
            # sleep has been inserted to before broadcasting operation

            if self.shutdown:
                break

            # edit: [action, character, ordered value, nodeid]
            # currentText: (character, ordered value, nodeid)
            while len(self.receivedOperations) > 0:
                edit = self.receivedOperations.pop(0)
                self.__currentText, self.__history = handle_new_edits(self.__currentText, edit, self.__history)
                
            #if self.__debug:
                #print(f"{self.__nodeID} is updated to {self.__currentText} \n")

            # insert one whole chunk
            print(f"{self.__nodeID} starting")
            while len(self.__tokenisedReferenceName) > 0:
                index = -1
                #find the node id value inside current text
                for i in range(len(self.__currentText)):
                   if self.__currentText[i][0] == str(self.__nodeID):
                       index = i
                       break

                # if index == -1:
                #     # TODO insert the node id
                #     # TODO update the index value
                   
                try:
                    valueRange = self.__currentText[index+2][1] - self.__currentText[index+1][1]
                except IndexError:
                    valueRange = 1.0 - self.__currentText[index+1][1]
                    
                finally:  
                    step = valueRange/(len(self.__tokenisedReferenceName)+1)
                    length = len(self.__tokenisedReferenceName)
    
                    for i in range(length):
                        editCharacter = self.__tokenisedReferenceName.pop(0)
                        editValue = (i+1)*step + self.__currentText[index+1][1]
                        edit = (setcommands.INSERT, editCharacter, editValue, self.__nodeID)
                        self.__currentText, self.__history = insert_operation(self.__currentText, edit, self.__history) # update local copy
                        time.sleep(round(random.uniform(0,5), 1)/1000)
                        self.send_to_nodes(self, edit) # broadcast to all connected nodes
                
                if self.__debug:
                    print(f"{self.__nodeID} has completed insertion. Updated state {self.__currentText} \n")

            
            # delete the respective strings
            while(self.__allowedToDelete and len(self.__deletingIndices) > 0):

                # find the first string to be deleted
                position = None
                deleteIndex = self.__deletingIndices.pop(0)
                nextIndex = deleteIndex + 1
                for i in range(len(self.__currentText)):
                    if self.__currentText[i][0] == str(deleteIndex):
                        position = i
                        if self.__debug:
                            print(f"{self.__nodeID} has found the index string to delete at {position} \n")
                        break

                if position != None:
                    try:
                        while self.__currentText[position+2][0] != str(nextIndex):
                            if self.__debug:
                                print(f"{self.__nodeID} is deleting {self.__currentText[position+2]}")
                            edit = (setcommands.DELETE, self.__currentText[position+2][0], self.__currentText[position+2][1], self.__currentText[position+2][2])
                            self.__currentText, self.__history = delete_operation(self.__currentText, edit, self.__history) # update local copy
                            time.sleep(round(random.uniform(0,5), 1)/1000)
                            self.send_to_nodes(self, edit) # broadcast to all connected nodes
                        if self.__debug:
                            print(f"{self.__nodeID} has completed deletion normally. Updated state {self.__currentText} \n")
                        break #reset the entire loop
                    except IndexError:
                        if self.__debug:
                            print(f"{self.__nodeID} has completed deletion of the last string. Updated state {self.__currentText} \n")
                        break # reset the entire loop
                if self.__debug:
                    print(f"{self.__nodeID} unable to find the index to delete")
            if(self.__allowedToDelete and len(self.__deletingIndices) > 0):
                continue
            
            if len(self.receivedOperations) > 0:
                self.completed = False
            else:
                self.completed = True

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