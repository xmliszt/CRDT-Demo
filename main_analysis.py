import argparse
import subprocess

parser = argparse.ArgumentParser(
    description="Run analysis for P2P Operation-based CRDT experiments")
parser.add_argument('-s',
                    '--start',
                    type=int,
                    default=2,
                    help="Start number of peers")
parser.add_argument('-m',
                    '--max',
                    type=int,
                    default=30,
                    help="Maximum number of peers")
parser.add_argument('-n', type=int, default=1, help="Number of experiments")

args = parser.parse_args()

s = args.start
m = args.max
n = args.n

for _ in range(n):
    try:
        subprocess.call(['python', 'graph.py', str(s), str(m)])
    except Exception as e:
        print(e)
        continue
