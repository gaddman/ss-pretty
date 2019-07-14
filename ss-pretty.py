#!/usr/bin/env python
# run ss and print the output nicely
# Chris Gadd
# https://github.com/gaddman/ss-pretty
# 2019-03-20

from __future__ import print_function
import argparse
import re
import select
import signal
import subprocess
import sys
import tty
import termios
import time
from datetime import datetime

# Function to poll for keypresses with timeout and without displaying character
def getKeypress(timeout):
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        # setraw affects STDOUT, so any print statements will need "\r" to add a LF
        # https://stackoverflow.com/a/26029573/3592326
        tty.setraw(fd)
        ready, _, _ = select.select([sys.stdin], [], [], timeout)
        if ready:
            return sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


# Field size mapping (for nice looking output)
widths = {
    "timestamp": 12,
    "local": 21,  # 21 good for IPv4
    "peer": 21,  # 21 good for IPv4
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
    timestamp,local,peer,mss,rcvmss,advmss,rto,rtt,cwnd,ssthresh,bytes_acked,
    unacked,retrans,send,pacing_rate,delivery_rate,busy,rcv_space,notsent

Example, showing just data rates:
    prettySS.py -f 'src 203.0.113.254:80' -u 0.5 -d 'timestamp,pacing_rate'
While running, press:
    h to repeat the header line
    v to toggle verbose
    q to quit""",
)
parser.add_argument(
    "-d",
    help="Comma-separated list of fields to display (see ss output or man)",
    default="timestamp,local,peer,mss,rcvmss,advmss,rto,rtt,cwnd,ssthresh,bytes_acked,unacked,retrans,send,pacing_rate,delivery_rate,busy,rcv_space,notsent",
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

# Verify fields
for key in showfields.split(","):
    if key not in widths:
        print("'{}' is not a valid field, use one of:".format(key))
        print(", ".join(widths))
        sys.exit()


# Print header
def printHeader():
    for thisfield in showfields.split(","):
        print("{:{width}}".format(thisfield, width=widths.get(thisfield)), end=" ")
    print("\r")


printHeader()

sscommand = ["ss", "-tmi", filter]

if duration is not None:
    endTime = time.time() + duration

while True:
    fields = {}
    # Timestamp isn't accurate to the packet arrival time so chop the last 3 chars off
    # to truncate to millisecond accuracy
    timestamp = datetime.now().time()
    fields["timestamp"] = str(timestamp)[:-3]
    # Execute ss command and loop through the output, skipping the header
    try:
        output = subprocess.check_output(sscommand).splitlines()
    except subprocess.CalledProcessError as e:
        sys.exit("Failed to run ss")
    except KeyboardInterrupt:
        sys.exit()
    output = iter(output[1:])
    for line in output:
        # IP addresses/ports
        line = line.decode()
        if verbose:
            print("\n" + line)
        local, peer = re.search(
            r"([0-9a-f\.:\[\]]+:\w+)\s+([0-9a-f\.:\[\]]+:\w+)", line
        ).groups()
        fields["local"] = local
        fields["peer"] = peer
        # Kernel data
        line = next(output).decode()
        if verbose:
            print(line)
        # Parse the kernel data line
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
        # Output all selected fields
        for thisfield in showfields.split(","):
            print(
                "{:{width}}".format(
                    fields.get(thisfield, ""), width=widths.get(thisfield)
                ),
                end=" ",
            )
        print("\r")

    if duration is not None and time.time() >= endTime:
        break

    # check for keypresses while waiting for next output
    char = getKeypress(frequency)
    if char is not None:
        if char == "h":
            # print header line
            printHeader()
        elif char == "v":
            # toggle verbose mode
            verbose = not verbose
        elif char == "q" or char == "\x03":
            # quit. \x03 = Ctrl-C
            sys.exit()
