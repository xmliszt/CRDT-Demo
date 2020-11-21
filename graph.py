from Peer import Peer
from time import sleep, time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import matplotlib.pyplot as plt
from utils import merge_operations
from random import randint, choice
import commands
from threading import Thread
from functools import partial
import os
import json
import csv
import resource
import sys

# Create N nodes
# Inter-connect all nodes
# Each node send one operation and makes all operations concurrent
# Time the duration from starting concurrent operation to reaching eventual consistency

# Graphs
# Time taken against number of concurrent operations
# Time taken against number of peers

# Set hard limit for file descriptor
resource.setrlimit(resource.RLIMIT_NOFILE, (12288, 12288))

FROM_PEERS = int(sys.argv[1])
MAX_PEERS = int(sys.argv[2])
INIT_PORT = 8000
HOST = "0.0.0.0"
TERMINATION_INIT_TIME = 8  # seconds
PEER_STOPPING_TIME = 8  # seconds
MONITOR_TIMEOUT = 3  # seconds

peers_x = []
peers_y = []
concurrent_operations_x = []
concurrent_operations_y = []


def dprint(s):
    print(f"[{datetime.now()}]: {s}")


def peer_send_msg(peer, operations):
    while len(operations) > 0:
        op = operations.pop(0)
        operation = op[0]
        val = op[1]
        data = ""
        sleep(randint(1, 1000) / 1000)  # simulate various network delay
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


def is_same(l):
    first = 0
    second = 1
    while second < len(l):
        if l[first] == l[second]:
            first += 1
            second += 1
        else:
            return False
    return True


def check_counters(peers):
    start_time = time() * 1000
    _timeout_count = 0
    while True:
        sleep(0.5)
        counts = list(map(lambda x: x.counter, peers))
        if is_same(counts):
            sleep(MONITOR_TIMEOUT)  # timeout
            _timeout_count += 1
            counts = list(map(lambda x: x.counter, peers))
            if is_same(counts):
                break
    end_time = time() * 1000
    time_taken = (end_time - start_time -
                  _timeout_count * MONITOR_TIMEOUT * 1000)
    peers_y.append(time_taken)
    dprint(
        f"Took {time_taken} ms. Monitor closed. Universal counter value: {counts[0]}"
    )


if __name__ == "__main__":

    for number_of_peers in range(FROM_PEERS, MAX_PEERS + 1):

        peers_x.append(number_of_peers)

        # Init peers
        dprint(f"Initializing {number_of_peers} peers...")
        peers = []
        port = INIT_PORT
        tmp_init_port = port
        for _ in range(number_of_peers):
            _peer = Peer(HOST, port)
            peers.append(_peer)
            _peer.start()
            port += 1
        INIT_PORT = port
        dprint(f"Initializing {number_of_peers} peers done!")

        # Interconnection
        dprint(f"Establishing interconnections for {number_of_peers} peers...")
        for i, p in enumerate(peers):
            for idx in range(number_of_peers):
                if i != idx:
                    p.connect_with_node(HOST, tmp_init_port + idx)
                    dprint(
                        f"Peer {p.port} connected with {tmp_init_port + idx}")
        dprint(f"Interconnection for {number_of_peers} peers is done!")

        # Performing operations

        operations = []
        for _ in range(number_of_peers):
            val = randint(1, 10)
            op = choice(['i', 'd', 'm', 'l'])
            operations.append((op, val))

            # Start Monitoring Counters
        dprint(f"Start monitoring the counters...")
        _monitor = Thread(target=partial(check_counters, peers))
        _monitor.start()
        _futures = []
        dprint(f"Sending concurrent operations...")
        with ThreadPoolExecutor(max_workers=number_of_peers) as executor:
            for peer in peers:
                _futures.append(
                    executor.submit(partial(peer_send_msg, peer), operations))

        sleep(8)
        for _future in _futures:
            _future.result()

        # Tear Down
        dprint(f"Closing peers...")
        for _peer in peers:
            _peer.stop()

        sleep(TERMINATION_INIT_TIME +
              PEER_STOPPING_TIME * max(1, number_of_peers // 10))

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.plot(peers_x, peers_y, 'go-', alpha=0.5)
    ax.set_title(
        "Time Taken to Reach Eventual Consistency (ms) agains Number of Peers")
    ax.set_xlabel("Number of peers")
    ax.set_ylabel("Time Taken to reach eventual consistency (ms)")

    if not os.path.exists("figures"):
        os.mkdir("figures")
    if not os.path.exists("raw"):
        os.mkdir("raw")
    if not os.path.exists("csv"):
        os.mkdir("csv")

    _counter = 1
    figure_path = os.path.join(
        "figures", f"peer_{FROM_PEERS}-{MAX_PEERS}_{_counter}.png")
    raw_path = os.path.join("raw",
                            f"peer_{FROM_PEERS}-{MAX_PEERS}_{_counter}.json")
    csv_path = os.path.join("csv",
                            f"peer_{FROM_PEERS}-{MAX_PEERS}_{_counter}.csv")
    while os.path.isfile(figure_path):
        _counter += 1
        figure_path = os.path.join(
            "figures", f"peer_{FROM_PEERS}-{MAX_PEERS}_{_counter}.png")
        raw_path = os.path.join(
            "raw", f"peer_{FROM_PEERS}-{MAX_PEERS}_{_counter}.json")
        csv_path = os.path.join(
            "csv", f"peer_{FROM_PEERS}-{MAX_PEERS}_{_counter}.csv")

    plt.savefig(figure_path, format='png')

    with open(raw_path, 'w', encoding='utf-8') as fp:
        json.dump({"peer_x": peers_x, "peer_y": peers_y}, fp)

    with open(csv_path, 'w', encoding='utf-8', newline='') as fh:
        writer = csv.writer(fh)
        writer.writerow([
            "Number of Peers", "Time Taken to Reach Eventual Consistency (ms)"
        ])
        for _each in list(zip(peers_x, peers_y)):
            writer.writerow(list(_each))

    dprint(
        f"Experiment peer_{FROM_PEERS}-{MAX_PEERS}_{_counter} is completed!")
