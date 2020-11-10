import commands
from time import sleep
from random import randint
import sys


def get_operation():
    print('''
  Choose an operation from below to perform:
  I1: Increment counter by 1
  D1: Decrement counter by 1
  M1: Multiply counter by 1
  L1: Divide counter by 1
  In: Increment counter by n, n is a custom integer
  Dn: Decrement counter by n, n is a custom integer
  Mn: Multiply counter by n, n is a custom integer
  Ln: Divide counter by n, n is a custom integer
  ''')
    choice = input("Your choice of operation: ")
    try:
        o = choice.lower()[0]
        n = int(choice.strip(" ")[1:])
        if o not in ['i', 'd', 'm', 'l']:
            raise Exception
        return (o, n)
    except Exception:
        print("Invalid operation format!")
        return False


def get_number_of_concurrent_operations(peers):
    sleep(2)
    _n = input(
        f"Enter the number of concurrent operations you want to perform or <Enter> to quit: "
    )
    if _n == "":
        print("Shutdown...")
        for p in peers:
            p.shutdown = True
            p.stop()
        sys.exit()
    try:
        _n = int(_n)
        if _n < 1:
            print("Must have at least 1 operation!")
            return False
        return _n
    except ValueError:
        print("Must be integer!")
        return False


def get_peer(n, peers):
    _id = input(f"Enter the peer ID to be controlled [1 - {n}]: ")
    try:
        _id = int(_id)
        if 1 <= _id <= n:
            return peers[_id - 1]
        else:
            print("Peer ID out of range!")
            return False
    except ValueError:
        print("Must be integer!")
        return False


def print_peers_and_counter(peers):
    print("")
    for idx, p in enumerate(peers):
        print(f"Peer ID: {idx+1}\tCounter value: {p.counter}")
    print("")


def thread_send_msg(peer, delay, operations):
    while len(operations) > 0:
        op = operations.pop()
        sleep(randint(1, delay) / 1000)  # simulate various network delay
        operation = op[0]
        val = op[1]
        data = ""
        if operation == 'i':
            data = f"Update >>> {commands.INCREMENT}{val}{commands.INCREMENT}"
        elif operation == 'd':
            data = f"Update >>> {commands.DECREMENT}{val}{commands.DECREMENT}"
        elif operation == 'm':
            data = f"Update >>> {commands.MULTIPLY}{val}{commands.MULTIPLY}"
        elif operation == 'l':
            data = f"Update >>> {commands.DIVIDE}{val}{commands.DIVIDE}"
        peer.operations = merge_operations(peer.operations, data)
        peer.send_to_nodes(data, exclude=peer.nodes_inbound)


def merge_operations(operations, data):
    if commands.INCREMENT in data:
        operations.append(data)
    elif commands.DECREMENT in data:
        operations.append(data)
    elif commands.MULTIPLY in data:
        operations.insert(0, data)
    elif commands.DIVIDE in data:
        operations.insert(0, data)
    return operations
