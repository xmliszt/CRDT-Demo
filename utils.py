import commands
from time import sleep
from random import randint
import sys

def get_operation():
  print('''
  Choose an operation from below to perform:
  I1: Increment counter by 1
  D1: Decrement counter by 1
  In: Increment counter by n, n is a custom integer
  Dn: Decrement counter by n, n is a custom integer
  ''')
  choice = input("Your choice of operation: ")
  o = choice.lower()[0]
  n = int(choice.strip(" ")[1:])
  return (o, n)

def get_number_of_concurrent_operations(peers):
  _n = input(f"Enter the number of concurrent operations you want to perform or <Enter> to quit: ")
  if _n == "":
    print("Shutdown...")
    for p in peers:
      p.stop()
    sys.exit()
  try:
    _n = int(_n)
    return _n
  except ValueError:
    print("Must be integer!")
    return False

def get_peer(n, peers):
  _id = input(f"Enter the peer ID to be controlled [1 - {n}]: ")
  return peers[int(_id)-1]

def print_peers_and_counter(peers):
  print("")
  for idx, p in enumerate(peers):
    print(f"Peer ID: {idx+1}\tCounter value: {p.counter}")
  print("")

def thread_send_msg(peer, delay, operations):
  while len(operations) > 0:
    op = operations.pop()
    sleep(randint(1, delay)/1000) # simulate various network delay
    operation = op[0]
    val = op[1]
    if operation == 'i':
      peer.send_to_nodes(f"Update >>> {commands.INCREMENT}{val}{commands.INCREMENT}", exclude=peer.nodes_inbound)
      peer.counter += val
    elif operation == 'd':
      peer.send_to_nodes(f"Update >>> {commands.DECREMENT}{val}{commands.DECREMENT}", exclude=peer.nodes_inbound)
      peer.counter -= val