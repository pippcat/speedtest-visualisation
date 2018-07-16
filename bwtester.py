#!/usr/bin/env python

import subprocess
import json
import threading
import Queue
import time
from datetime import datetime
import math

INTERVAL = 1         #   1 second
AVG_LOW_PASS = 0.2      #   Simple Complemetary Filter
FILENAME = "data.csv"   #   where to store data?

ifaces = {}

def GetNetworkInterfaces():
    ifaces = []
    f = open("/proc/net/dev")
    data = f.read()
    f.close()
    data = data.split("\n")[2:]
    for i in data:
        if len(i.strip()) > 0:
            x = i.split()
            # Interface |                        Receive                          |                         Transmit
            #   iface   | bytes packets errs drop fifo frame compressed multicast | bytes packets errs drop fifo frame compressed multicast
            k = {
                "interface" :   x[0][:len( x[0])-1],   
                "tx"        :   {
                    "bytes"         :   int(x[1]),
                    "packets"       :   int(x[2]),
                    "errs"          :   int(x[3]),
                    "drop"          :   int(x[4]),
                    "fifo"          :   int(x[5]),
                    "frame"         :   int(x[6]),
                    "compressed"    :   int(x[7]),
                    "multicast"     :   int(x[8])
                },
                "rx"        :   {
                    "bytes"         :   int(x[9]),
                    "packets"       :   int(x[10]),
                    "errs"          :   int(x[11]),
                    "drop"          :   int(x[12]),
                    "fifo"          :   int(x[13]),
                    "frame"         :   int(x[14]),
                    "compressed"    :   int(x[15]),
                    "multicast"     :   int(x[16])
                }
            }
            ifaces.append(k)
    #print ifaces
    return ifaces

def speedtest(foo):
    print "Starting speed test"
    batcmd="/usr/bin/speedtest-cli --json"
    result = subprocess.check_output(batcmd, shell=True)
    database = json.loads(result)
#    print json.dumps(database, indent=4, sort_keys=True)
    return result

def bandwidth(bla):
    print "Loading Network Interfaces"
    idata = GetNetworkInterfaces()
    print "Filling tables"
    for eth in idata:
        ifaces[eth["interface"]] = {
            "rxrate"    :   0,
            "txrate"    :   0,
            "avgrx"     :   0,
            "avgtx"     :   0,
            "toptx"     :   0,
            "toprx"     :   0,
            "sendbytes" :   eth["tx"]["bytes"],
            "recvbytes" :   eth["rx"]["bytes"]
        }
        
    for i in range(30):
        idata = GetNetworkInterfaces()
        for eth in idata:
            #   Calculate the Rate
            ifaces[eth["interface"]]["rxrate"]      =   (eth["rx"]["bytes"] - ifaces[eth["interface"]]["recvbytes"]) / INTERVAL
            ifaces[eth["interface"]]["txrate"]      =   (eth["tx"]["bytes"] - ifaces[eth["interface"]]["sendbytes"]) / INTERVAL
        
            #   Set the Max Rates
            ifaces[eth["interface"]]["toprx"]       =   ifaces[eth["interface"]]["rxrate"] if ifaces[eth["interface"]]["rxrate"] > ifaces[eth["interface"]]["toprx"] else ifaces[eth["interface"]]["toprx"]
            ifaces[eth["interface"]]["toptx"]       =   ifaces[eth["interface"]]["txrate"] if ifaces[eth["interface"]]["txrate"] > ifaces[eth["interface"]]["toptx"] else ifaces[eth["interface"]]["toptx"]
            
        time.sleep(INTERVAL)
    result = {
        "wlp3s0":{
            "Download":str(float(ifaces["wlp3s0"]["toptx"])*8),
            "Upload":str(ifaces["wlp3s0"]["toprx"]*8)
        }
    }
    return result
 


que = Queue.Queue()
thread_list = list()
t = threading.Thread(target=lambda q, arg1: q.put(speedtest(arg1)), args=(que, 'bla'))
# Sticks the thread in a list so that it remains accessible
thread_list.append(t)
t = threading.Thread(target=lambda q, arg1: q.put(bandwidth(arg1)), args=(que, 'bla'))
thread_list.append(t)

# Starts threads
for thread in thread_list:
    thread.start()

# This blocks the calling thread until the thread whose join() method is called is terminated.
# From http://docs.python.org/2/library/threading.html#thread-objects
for thread in thread_list:
    thread.join()

# Demonstrates that the main process waited for threads to complete
print "Done"
# Check thread's return value
while not que.empty():
    result = que.get()
    print result
