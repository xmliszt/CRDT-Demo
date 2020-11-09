from time import sleep
from Peer import Peer

node = Peer('127.0.0.1', 8004)
node.start()
node.connect_with_node('127.0.0.1', 8001)
node.connect_with_node('127.0.0.1', 8002)
node.connect_with_node('127.0.0.1', 8003)

node.send_to_nodes("HELLOOOOOOOOO!")