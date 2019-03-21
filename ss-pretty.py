#!/usr/bin/env python3
# run ss and print the output nicely
# Chris Gadd
# https://github.com/gaddman/ss-pretty
# 2019-03-20

import argparse
import signal
import subprocess
import sys
import time
from datetime import datetime

# Register signal handler to exit gracefully if no time specified
def signal_handler(sig, frame):
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

# Field size mapping (for nice looking output)
widths = {
    "skmem": 60,
    "cong_alg": 8,
    "ts": 2,
    "sack": 4,
    "ecn": 3,
    "ecnseen": 7,
    "fastopen": 8,
    "wscale": 6,
    "rto": 4,
    "rtt": 15,
    "ato": 4,
    "mss": 4,
    "pmtu": 4,
    "rcvmss": 6,
    "advmss": 6,
    "cwnd": 6,
    "ssthresh": 9,
    "bytes_acked": 12,
    "bytes_received": 14,
    "segs_out": 8,
    "segs_in": 8,
    "data_segs_out": 13,
    "data_segs_in": 13,
    "send": 10,
    "Lastsend": 8,
    "lastrcv": 7,
    "lastack": 7,
    "pacing_rate": 11,
    "rcv_rtt": 7,
    "delivery_rate": 13,
    "busy": 6,
    "unacked": 7,
    "retrans": 7,
    "rcv_space": 9,
    "rcv_ssthresh": 12,
    "notsent": 8,
    "minrtt": 6,
}

# Parse arguments and set defaults
parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description="Just like running 'ss -tmi', but with a columnar format",
    epilog="""Default fields to display are:
    mss,rcvmss,advmss,rto,rtt,cwnd,ssthresh,bytes_acked,unacked,retrans,send,
    pacing_rate,delivery_rate,busy,rcv_space,notsent

Example, showing just data rates:
    prettySS.py -f 'src 203.0.113.254:80' -u 0.5 -d 'pacing_rate,delivery_rate'""",
)
parser.add_argument(
    "-d",
    help="Comma-separated list of fields to display (see ss output or man)",
    default="mss,rcvmss,advmss,rto,rtt,cwnd,ssthresh,bytes_acked,unacked,retrans,send,pacing_rate,delivery_rate,busy,rcv_space,notsent",
)
parser.add_argument("-f", help="Filter (as used by ss)", type=str, default="")
parser.add_argument(
    "-u", help="Update frequency (seconds, default=1)", type=float, default=1
)
parser.add_argument("-t", help="Time to run for (seconds, default=forever)", type=float)
parser.add_argument("-v", help="Verbose", action="store_true")
args = parser.parse_args()
verbose = args.v
showfields = args.d
filter = args.f
frequency = args.u
duration = args.t

# Print header and verfy fields
print("timestamp      ", end=" ")
for thisfield in showfields.split(","):
    try:
        print("{:{width}}".format(thisfield, width=widths.get(thisfield)), end=" ")
    except ValueError:
        print("\n'{}' is not a valid field".format(thisfield))
        sys.exit()
print()

sscommand = ["ss", "-tmi", filter]
if duration is not None:
    endTime = time.time() + duration

while True:
    output = subprocess.check_output(sscommand)
    timestamp = datetime.now().time()
    lines = output.splitlines()
    if len(lines) == 1:
        # only the header line
        continue
    else:
        # Just take the first line with data
        # (best make sure your filter only matches one line)
        line = lines[2].decode()
    if verbose:
        print(line)
    fields = {}
    chunks = line.split()  # split on space
    for index, chunk in enumerate(chunks):
        if ":" in chunk:
            # Most fields are key:value
            key, value = chunk.split(":")
            fields[key] = value
        elif "rate" in chunk or chunk == "send":
            # send, delivery_rate, and pacing_rate
            # have the key in one field and the value in the next
            key = chunk
            value = chunks[index + 1]
            fields[key] = value
        elif index == 1:
            # TCP algorithm is always the 2nd field
            key = "cong_alg"
            value = chunk
            fields[key] = value
    print("{}".format(timestamp), end=" ")
    for thisfield in showfields.split(","):
        print(
            "{:{width}}".format(fields.get(thisfield, ""), width=widths.get(thisfield)),
            end=" ",
        )
    print()
    if duration is not None and time.time() >= endTime:
        break
    else:
        time.sleep(frequency)
