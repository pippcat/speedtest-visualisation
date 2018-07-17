#!/usr/bin/env python3

import subprocess
import json
import threading
import Queue
import time
from datetime import datetime
import math
import speedtest
import csv
import sys

INTERVAL = 1         #   1 second
AVG_LOW_PASS = 0.2      #   Simple Complemetary Filter
FILENAME = "data.csv"   #   where to store data?
INTERNAL_NW = ""
EXTERNAL_NW = "enp0s25"

ifaces = {}
result = []

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
    import speedtest
    print "Starting speed test"
    time.sleep(5)
    s = speedtest.Speedtest()
    s.get_best_server()
    s.download()
    s.upload()
    results_dict = s.results.dict()
    print "Speedtest resultsr:"
    print results_dict
    return results_dict['timestamp'], results_dict['download']/1000000,  results_dict['upload']/1000000, results_dict['ping']

def bandwidth(foo):
    print "Starting Bandwidth measurement"
    idata = GetNetworkInterfaces()
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
        
    for i in range(40):
        idata = GetNetworkInterfaces()
        for eth in idata:
            #   Calculate the Rate
            ifaces[eth["interface"]]["rxrate"]      =   (eth["rx"]["bytes"] - ifaces[eth["interface"]]["recvbytes"]) / INTERVAL
            ifaces[eth["interface"]]["txrate"]      =   (eth["tx"]["bytes"] - ifaces[eth["interface"]]["sendbytes"]) / INTERVAL
        
            #   Set the Max Rates
            ifaces[eth["interface"]]["toprx"]       =   ifaces[eth["interface"]]["rxrate"] if ifaces[eth["interface"]]["rxrate"] > ifaces[eth["interface"]]["toprx"] else ifaces[eth["interface"]]["toprx"]
            ifaces[eth["interface"]]["toptx"]       =   ifaces[eth["interface"]]["txrate"] if ifaces[eth["interface"]]["txrate"] > ifaces[eth["interface"]]["toptx"] else ifaces[eth["interface"]]["toptx"]
            
        time.sleep(INTERVAL)
    download = ifaces[EXTERNAL_NW]["toptx"]*8
    upload = ifaces[EXTERNAL_NW]["toprx"]*8
    print "Bandwidth measurement result: Download " + str(download) + "b/s; Upload " + str(upload) + "b/s"
    return upload/1000000, upload/1000000
 


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
    result += que.get()
#print result
# result = [Timestamp, Speedtest Download, Speedtest Upload, Speedtest Ping, All Download, All Upload]
other_dl = result[4]-result[1]
other_ul = result[5]-result[2]
result.append(other_dl)
result.append(other_ul)
# result = [Timestamp, Speedtest Download, Speedtest Upload, Speedtest Ping, All Download, All Upload, Other Upload, Other Download]
with open(FILENAME,'a') as fout:
    writer = csv.writer(fout, delimiter = ';')
    writer.writerow(result)
