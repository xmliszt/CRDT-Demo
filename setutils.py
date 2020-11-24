# -*- coding: utf-8 -*-
"""
Created on Fri Nov 13 09:13:54 2020

@author: world
"""

import setcommands
import random
import sys

def append_operations_for_display(operations, data):
    operations.append(data)

# appends all incoming operations
def append_operations_for_edits(operations, data):
    operations.append(data)
    return operations

# for nodes to display their local copy
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
# edit: (action, character, ordered value, nodeid)
# history: (edit, historyIndex, successStatus: boolean)
# personalcopy: (character, ordered value, nodeid)
def handle_new_edits(personalCopy, newEdit, history):

    if newEdit[0] == setcommands.INSERT:
        personalCopy.append((newEdit[1], newEdit[2], newEdit[3]))
        newHistoryIndex = history[-1][1] + 1
        history.append((newEdit, newHistoryIndex, True))
        
    elif newEdit[0] == setcommands.DELETE:
        index = -1
        found = False
        for i in range(len(personalCopy)):
            if personalCopy[i][0] == newEdit[1] and personalCopy[i][1] == newEdit[2]:
                found = True
                index = i
                break
        if found:
            del personalCopy[index]
            newHistoryIndex = history[-1][1] + 1
            history.append((newEdit, newHistoryIndex, True))
        else:
            newHistoryIndex = history[-1][1] + 1
            history.append((newEdit, newHistoryIndex, False))
                
    # sort
    personalCopy.sort(key=lambda x: x[1])
    return personalCopy, history
    
# insert operation done by node to local copy
def insert_operation(personalCopy, insertionEdit, history):
    personalCopy.append((insertionEdit[1], insertionEdit[2], insertionEdit[3]))
    newHistoryIndex = history[-1][1] + 1
    history.append((insertionEdit, newHistoryIndex, True))
        
    # sort
    personalCopy.sort(key=lambda x: x[1])
    return personalCopy, history

# delete operation done by node to local copy    
def delete_operation(personalCopy, deletionEdit, history):
    index = -1
    found = False
    for i in range(len(personalCopy)):
        if personalCopy[i][0] == deletionEdit[1] and personalCopy[i][1] == deletionEdit[2]:
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

# input test decision
def input_test_decision(peers, fixedInput, deleteInput):
    
    print('''
      Choose a test mode from the list below: 
      0. Exit test
      1. A string containing all the indices of the nodes. Each node will try to insert their own names behind their corresponding index.
      2. Similar to 1, but the selected indices will have their names deleted.
      3. Given a blank string, each node try to add their number and name to it
      ''')
      
    #decision = input("Your choice of test: ")
    decision = fixedInput
    
    try:
        if decision not in ['0', '1', '2']:
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
        return (referenceTokenisedString, [-1])
    
    elif decision == '2':
        
        while True:
            #numberOfSelectedIndices = input("Choose how many strings to delete.")
            numberOfSelectedIndices = deleteInput
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
            
        print("The following indices will be deleted:", deletingIndices)
        
        step = 0.9/(len(peers)*2)
        referenceTokenisedString = []
        value = 0.1
        for i in range(len(peers)):
            referenceTokenisedString.append((str(i+1), value))
            value += step
            referenceTokenisedString.append((" ", value))
            value += step
            
        return (referenceTokenisedString, deletingIndices)

    else:
        pass

# completion condition    
def check_completion(peersList, peersStatusList):
    while True:
        for i in range(len(peersList)):
            if peersList[i].completed:
                peersStatusList[i] = True
            
        if all(x == True for x in peersStatusList):
            break
    return True

# appends final string to array for final checking
def add_final_string(peersFinalStringList, finalString):
    peersFinalStringList.append(finalString)
    return peersFinalStringList

# given array of all local copies of every node, check for convergence
def check_convergence(peersFinalStringList):
    metric = peersFinalStringList[0]
    status = True
    for i in peersFinalStringList:
        if i != metric:
            status = False
            break
    return status

# parses timing values for graph plotting later
def peer_convergence_values(allTimingsList):
    yValues = []
    xValues = []
    for i in range(len(allTimingsList)):
        average = 0
        for j in range(len(allTimingsList[i])):
            average += allTimingsList[i][j]
        average /= len(allTimingsList[i])
        yValues.append(average)
        xValues.append(i+2)
    return xValues, yValues
    