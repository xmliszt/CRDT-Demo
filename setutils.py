# -*- coding: utf-8 -*-
"""
Created on Fri Nov 13 09:13:54 2020

@author: world
"""

import setcommands
import random
import sys

# appends all incoming operations
def append_incoming_operations(operationsBuffer, data):
    operationsBuffer.append(data)
    return operationsBuffer

# appends outbound connection
def add_outbound_connection(outboundBuffer, nodeID):
    outboundBuffer.append(nodeID)
    return outboundBuffer

# tries to remove the node from outboundPeers buffer
def remove_outbound_connection(outboundBuffer, nodeID):
    try:
        outboundBuffer.remove(nodeID)
        return outboundBuffer, True
    except ValueError:
        return outboundBuffer, False
    
# tries to remove the node from inboundPeers buffer
def remove_inbound_connection(inboundBuffer, nodeID):
    try:
        inboundBuffer.remove(nodeID)
        return inboundBuffer, True
    except ValueError:
        return inboundBuffer, False
        
# appends inbound connection
def add_inbound_connection(inboundBuffer, nodeID):
    inboundBuffer.append(nodeID)
    return inboundBuffer

# returns the regularised version of the local text
def display_final_string(currentText):
    string = ""
    for i in range(len(currentText)):
        string += currentText[i][0]
    return string

# tokenises the name string into the array        
def tokenise_reference_name(nameString):
    tokenisedReferenceName = list(nameString)
    tokenisedReferenceName.append(" ")
    return tokenisedReferenceName
    
# given the new edit, update the personal copy of the text
# edit in the format of {"command": setcommands.INSERT, "character": editCharacter, "value": editValue, "nodeID": self._nodeID}
# add to the local history of this node with the format of (edit, historyIndex, boolean)
# new edits added into the personal copy: (editCharacter, editValue, self._nodeID)
def handle_new_edits(personalCopy, newEdit, history, deleteBuffer):

    if newEdit["command"] == setcommands.INSERT:
        personalCopy.append((newEdit["character"], newEdit["value"], newEdit["nodeID"]))
        newHistoryIndex = history[-1][1] + 1
        history.append((newEdit, newHistoryIndex, True))
        
    elif newEdit["command"] == setcommands.DELETE:
        index = -1
        found = False
        for i in range(len(personalCopy)):
            if personalCopy[i][0] == newEdit["character"] and personalCopy[i][1] == newEdit["value"]:
                found = True
                index = i
                break
        if found:
            del personalCopy[index]
            newHistoryIndex = history[-1][1] + 1
            history.append((newEdit, newHistoryIndex, True))
        else: # either has been deleted by me or does not exist yet
            previouslyDeleted = False
            for i in history[::-1]:
                if i[0] == newEdit: # deleted before
                    previouslyDeleted = True
                    break
            if not previouslyDeleted:
                deleteBuffer.append(newEdit)
                
    # sort
    personalCopy.sort(key=lambda x: x[1])
    return personalCopy, history, deleteBuffer
    
# handles local insertion operation
def insert_operation(personalCopy, insertionEdit, history):
    personalCopy.append((insertionEdit["character"], insertionEdit["value"], insertionEdit["nodeID"]))
    newHistoryIndex = history[-1][1] + 1
    history.append((insertionEdit, newHistoryIndex, True))
        
    # sort
    personalCopy.sort(key=lambda x: x[1])
    return personalCopy, history

# deletion edit has to be       
def local_delete_operation(personalCopy, deletionEdit, history):
    index = -1
    found = False
    for i in range(len(personalCopy)):
        if personalCopy[i][0] == deletionEdit["character"] and personalCopy[i][1] == deletionEdit["value"]:
            found = True
            index = i
            break
    if found:
        del personalCopy[index]
        newHistoryIndex = history[-1][1] + 1
        history.append((deletionEdit, newHistoryIndex, True))
    else:
        newHistoryIndex = history[-1][1] + 1
        history.append((deletionEdit, newHistoryIndex, False))
                
    # sort
    personalCopy.sort(key=lambda x: x[1])
    return personalCopy, history

        
def input_test_decision(peers):
    
    print('''
      Choose a test mode from the list below: 
      0. Exit test
      1. A string containing all the indices of the nodes. Each node will try to insert their own names behind their corresponding index.
      2. Similar to 1, but the selected indices will have their names deleted.
      3. Choose one node to be put to long sleep during execution and awaken after a while, under the test situation of 1
      ''')
      
    decision = input("Your choice of test: ")
    try:
        if decision not in ['0', '1', '2', '3']:
            raise Exception 
    except Exception:
        print("Invalid decision!")
        return False
    
    if decision == '0':
        print("Shutting down...")
        for p in peers:
            p.shutdown = True
            p.stop()
        sys.exit()
        
    if decision == '1':
        step = 0.9/(len(peers)*2)
        referenceTokenisedString = []
        value = 0.1
        for i in range(len(peers)):
            referenceTokenisedString.append((str(i+1), value))
            value += step
            referenceTokenisedString.append((" ", value))
            value += step
        return (referenceTokenisedString, [-1], -1, decision)
    
    elif decision == '2':
        
        while True:
            numberOfSelectedIndices = input("Choose how many strings to delete: ")
            if not numberOfSelectedIndices.isdigit():
                print("Invalid input!")
                continue
            if int(numberOfSelectedIndices) < 0 or int(numberOfSelectedIndices) > len(peers):
                print("Out of range!")
                continue
            print("The test will randomly generate the indices to be deleted.")
            break
        
        # generate
        deletingIndices = []
        for i in range(int(numberOfSelectedIndices)):
            deletingIndices.append(random.randint(1, len(peers)))
            
        print("The following indices will be deleted: ", deletingIndices)
        
        step = 0.9/(len(peers)*2)
        referenceTokenisedString = []
        value = 0.1
        for i in range(len(peers)):
            referenceTokenisedString.append((str(i+1), value))
            value += step
            referenceTokenisedString.append((" ", value))
            value += step
            
        return (referenceTokenisedString, deletingIndices, -1, decision)
    
    elif decision == '3':
        while True:
            sleepingNode = input("Choose the node to sleep: ")
            if not sleepingNode.isdigit():
                print("Invalid input!")
                continue
            if int(sleepingNode) < 0 or int(sleepingNode) > len(peers):
                print("Out of range!")
                continue
            print("The selected node will be put to sleep.")
            break
        
        step = 0.9/(len(peers)*2)
        referenceTokenisedString = []
        value = 0.1
        for i in range(len(peers)):
            referenceTokenisedString.append((str(i+1), value))
            value += step
            referenceTokenisedString.append((" ", value))
            value += step
        return (referenceTokenisedString, [-1], int(sleepingNode), decision)
    else:
        pass
    
def check_completion(peersList, peersStatusList):
    while True:
        for i in range(len(peersList)):
            if peersList[i]._completed:
                peersStatusList[i] = True
            
        if all(x == True for x in peersStatusList):
            break
    return True
    

