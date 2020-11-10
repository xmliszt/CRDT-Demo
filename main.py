from Peer import Peer
from datetime import datetime
import argparse

DEBUG = 0  # 1 to on debug, 0 to off debug
HOST = '0.0.0.0'


def debug_log(msg):
    if DEBUG:
        print(f"[{datetime.now()}]: {msg}")


parser = argparse.ArgumentParser(
    description="Demo on operation-based CRDT via P2P network")
parser.add_argument('-p',
                    type=int,
                    default=8001,
                    help='Port number of the peer')

args = parser.parse_args()
PORT = args.p

if __name__ == "__main__":

    p = Peer(HOST, PORT)
    p.start()
    print(f"Peer is running on {HOST}:{PORT}")

    if DEBUG:
        debug_log(p.all_nodes)