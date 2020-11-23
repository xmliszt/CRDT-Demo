# -*- coding: utf-8 -*-
"""
Created on Fri Nov 13 09:13:54 2020

@author: world
"""

import setcommands
from time import sleep
import random
from random import randint
import sys
import copy

def append_operations_for_display(operations, data):
    operations.append(data)

# appends all incoming operations
def append_operations_for_edits(operations, data):
    
    operations.append(data)
    
    return operations

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
# edit in the format of (action, character, ordered value, nodeid)
# add to the local history of this node with the format of (edit, historyIndex, successStatus: boolean)
# new edits added into the personal copy: (character, ordered value, nodeid)
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
    
def insert_operation(personalCopy, insertionEdit, history):
    personalCopy.append((insertionEdit[1], insertionEdit[2], insertionEdit[3]))
    newHistoryIndex = history[-1][1] + 1
    history.append((insertionEdit, newHistoryIndex, True))
        
    # sort
    personalCopy.sort(key=lambda x: x[1])
    return personalCopy, history

        
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

        
def input_test_decision(peers):
    
    print('''
      Choose a test mode from the list below: 
      0. Exit test
      1. A string containing all the indices of the nodes. Each node will try to insert their own names behind their corresponding index.
      2. Similar to 1, but the selected indices will have their names deleted.
      3. Given a blank string, each node try to add their number and name to it
      ''')
      
    decision = input("Your choice of test: ")
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
            numberOfSelectedIndices = input("Choose how many strings to delete.")
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
    
def check_completion(peersList, peersStatusList):
    while True:
        for i in range(len(peersList)):
            if peersList[i].completed:
                peersStatusList[i] = True
            
        if all(x == True for x in peersStatusList):
            break
    return True
    

# lsti = [1,2,3]
# index = 0
# final = 4
# while True:
#     try:
#         while(lsti[index] != final):
#             lsti.pop(0)
#             print("lsti status", lsti)
#         break
#     except IndexError:
#         print("error check status", lsti)
#         break
# print("outside", lsti)
    

'''
# request for input from the user on the text to be completed
# returns a tuple of texts 
def input_text(peers):
    text = input(
        f"Enter the final text that you want all peers to complete or press <Enter> to quit: "
        )
    
    # no inputs
    if text == "":
        print("Shutting down...")
        for p in peers:
            p.shutdown = True
            p.stop()
        sys.exit()
        
    elif len(text) == 1:
        print("The text must be at least 2 characters long!")
        return False
    
    elif type(text) != str:
        print("Only strings are accepted")
        return False
    
    return text


# valid input text provided, allow for user to make decision on the operations to be completed
# returns tuple of (complete text as reference, incomplete text for peers to update)
# each element in incomplete text: (character, orderedValue)
def input_text_decision(text):
        

          Choose a mode of operation from the list below:
          1: All peers are given the full text as reference and tries to recreate it from scratch together.
          2. All peers are given the full text as reference, as well as the incomplete text for all the peers to complete together.

          
    decision = input("Your choice of operation: ")
    try:
        if decision not in ['1', '2']:
            raise Exception 
    except Exception:
        print("Invalid decision!")
        return False
    
    # if 1 is selected
    if decision == '1':
        # provide full text and incomplete text with only first and last character filled in
        # [(letter, value), (letter, value)]
        tokenisedFullText = list(text)
        tokenisedIncompleteText = []
        tokenisedIncompleteText.append((tokenisedFullText[0], 0.1))
        tokenisedIncompleteText.append((tokenisedFullText[-1], 0.9))
        return (tokenisedFullText, tokenisedIncompleteText)
    
    # if 2 is selected
    else:
        tokenisedFullText = list(text)
        
        # just delete the first character
        if len(tokenisedFullText) == 2 or len(tokenisedFullText) == 3:
            
            temp = copy.deepcopy(tokenisedFullText)
            temp.pop(0)
            tokenisedIncompleteText = []
            step = 0.9/len(temp)
            
            for i in range(len(temp)):
                tokenisedIncompleteText.append((temp[i], 0.1+i*step))

            return (tokenisedFullText, tokenisedIncompleteText)
        
        # delete first quarter, second half alternate delete
        else:
            deleteQuarterIndex = int(len(tokenisedFullText) / 4)
            
            # delete first quarter
            quarterString = text[deleteQuarterIndex::]

            # delete alternate in second half
            halfIndex = int(len(quarterString) / 3)
            incompleteString = text[halfIndex::2] 
            temp = list(incompleteString)
            step = 0.9/len(temp)
            tokenisedIncompleteText = []
            
            for i in range(len(temp)):
                tokenisedIncompleteText.append((temp[i], 0.1+i*step))
            
            return (tokenisedFullText, tokenisedIncompleteText)


'''
'''
cases:
    all users try to complete a full text
    input: your final text (or what you want all nodes to try and achieve) or blank
    input: types of behaviour:
            if blank: all peers will try to complete it, subject to their own constraints determined by random
            if not blank: chunks will be removed for peers to try and fill in, subject to their own constraints determined by random
            
            
    operations:
        insert, delete
            
    input text is converted into list, tokenise characters, passed to each node
    each node will randint: which operation to do (only one allowed), number of characters allowed (delete: pick minimum, insert: follow necessary. \
        if end text, end early and request termination until all respond)
    , how long to sleep for. characters are limited to ascii (no new line or moving around)
    priority:
        1. if duplicate character: delete (from right to left), if multiple rounds already, reduce likelihood to getting delete for particular node
        2. if insert character, just insert according to difference with input text
        3. on completion status on any node, send operation with request for termination. once all respond affirmative, initiate end prints for output node
        
    each node to have:
        function to update their own local version when given operation/id log
        create operation/id log for output node to parse + other nodes to parse
        track personal operations log
        track received operations log (not from me)
            
     
    text
    [token, nodeid]
    
    operation
    [action, token, nodeid, nodeid of the previous character]
    [ins, new token, new nodeid, nodeid of previous character] last writer wins
    [del, old token, old nodeid, nodeid of previous character] delete specific id, if none, return not found and update state
    look into adversary
    
    [action, character, ordered value, nodeid]
    
    
    do what????
    given a text, each node will try to complete the entire text together
    refresh before each insert, either one chunk quick inserts or indiv inserts 
    
    
    random input per peer
    fixed input per peer
    option 1
    1 2 3 per node given a name, try to insert their names in at the same time, all operations propagated at different time
    -> check eventual state
    option 2
    fix delete something let choose which number's string to delete
    
'''