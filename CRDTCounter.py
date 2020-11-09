from time import sleep
from Peer import Peer
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from utils import get_operation, get_peer, print_peers_and_counter, get_number_of_concurrent_operations, thread_send_msg

DEBUG = 0 # 1 to on debug, 0 to off debug
HOST = '0.0.0.0'
PORT_INIT = 8000
DELAY = 1000 # Simulate internet delay from sender to receiver in ms

def debug_log(msg):
  if DEBUG:
    print(f"[{datetime.now()}]: {msg}")

if __name__ == "__main__":
  n = input("Enter the number of peers in the P2P network: ")
  n = int(n)
  if n < 2: raise Exception("Should have at least 2 peers")
  elif n > 50: raise Exception("Please demo using less than 50 peers for message displaying purposes!")
  peers = []  # To input all the peers
  for i in range(n):
    p = Peer(HOST, PORT_INIT+i+1)
    peers.append(p)
    p.start()
  
  # set up p2p connection
  for i, p in enumerate(peers):
    for idx in range(n):
      if i != idx:
        p.connect_with_node(HOST, PORT_INIT+idx+1)

  if DEBUG:
    for i in peers:
      debug_log(i.all_nodes)

  print(f"You have successfully set up {len(peers)} peers with id ranging from 1 to {n}")
  print("Each peer has a counter value initialized to be 0")

  while True:

    sleep(DELAY/1000)
    print_peers_and_counter(peers)

    _n = get_number_of_concurrent_operations(peers)
    operations = []
    active_peers = []
    if not _n:
      continue
    for _ in range(_n):
      peer = get_peer(n, peers)
      o, val = get_operation()
      operations.append((o, val))
      active_peers.append(peer)

    with ThreadPoolExecutor(max_workers=_n) as worker:
      for p in active_peers:
        worker.submit(partial(thread_send_msg, p, DELAY), operations)
    


  