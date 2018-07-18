#!/usr/bin/env python3

import queue
import threading
import psutil
import csv
import time
import os

from datetime import datetime

result = []
filename = "data.csv" # name of file where data is stored
external = "eth0" # name of network interface connected to the internet
internal = "eth1" # name of network interface connected to the LAN

def bw(direction): # function to measure bandwidth usage
	interval = 2 # measurement interval
	time.sleep(10) # to make sure speedtest already started
	before = psutil.net_io_counters(pernic=True)
	external_before = before[external]
	internal_before = before[internal]
	external_rv_before = external_before[1]
	external_tx_before = external_before[0]
	internal_rv_before = internal_before[1]
	internal_tx_before = internal_before[0]

	time.sleep(interval)

	after = psutil.net_io_counters(pernic=True)
	external_after = after[external]
	internal_after = after[internal]
	external_rv_after = external_after[1]
	external_tx_after = external_after[0]
	internal_rv_after = internal_after[1]
	internal_tx_after = internal_after[0]
	if direction=="dl":
		external_rv_per_sec = (external_rv_after - external_rv_before) / interval / 1000000 * 8
		internal_rv_per_sec = (internal_rv_after - internal_rv_before) / interval / 1000000 * 8
		print("BW DL test done. external_rv_per_sec = " + str(external_rv_per_sec) + "; internal_rv_per_sec = " + str(internal_rv_per_sec))
		return [external_rv_per_sec, internal_rv_per_sec]
	elif direction=="ul":
		external_tx_per_sec = (external_tx_after - external_tx_before) / interval / 1000000 * 8
		internal_tx_per_sec = (internal_tx_after - internal_tx_before) / interval / 1000000 * 8
		print("BW UL test done. external_tx_per_sec = " + str(external_tx_per_sec) + "; internal_tx_per_sec = " + str(internal_tx_per_sec))
		return [external_tx_per_sec, internal_tx_per_sec]

def speedtest(direction): # does the speed test to use the full external network bandwidth
	import speedtest
	s = speedtest.Speedtest()
	s.get_best_server()
	if direction=="dl":
		s.download()
	elif direction=="ul":
		s.upload()
	else:
		print("error")
	results_dict = s.results.dict()
	if direction=="dl":
		print("Speedtest DL test done. ping = " + str(results_dict['ping']) + "ms; external DL speed = " + str(results_dict['download']/1000000))
		return [results_dict['ping'], results_dict['download']/1000000]
	elif direction=="ul":
		print("Speedtest UL test done. ping = " + str(results_dict['ping']) + "ms; external UL speed = " + str(results_dict['upload']/1000000))
		return [results_dict['ping'], results_dict['upload']/1000000]

# we have to use multitasking to do the bandwidth measurement during the speed test
que = queue.Queue() # the queue collects the results of the different threads
dl_thread_list = list() # two different thread lists to be able to do things sequentially
ul_thread_list = list()
dl = threading.Thread(target=lambda q, arg1: q.put(speedtest(arg1)), args=(que, 'dl'))
dl_thread_list.append(dl)
dl = threading.Thread(target=lambda q, arg1: q.put(bw(arg1)), args=(que, 'dl'))
dl_thread_list.append(dl)

for thread in dl_thread_list:
	thread.start() # let's do some multitasking

result.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) # timestamp is first entry in the result list

for thread in dl_thread_list:
	thread.join() # wait until threads have done their work

while not que.empty():
	result.extend(que.get()) # append results to result list

# same thing, this time for upload:
ul = threading.Thread(target=lambda q, arg1: q.put(speedtest(arg1)), args=(que, 'ul'))
ul_thread_list.append(ul)
ul = threading.Thread(target=lambda q, arg1: q.put(bw(arg1)), args=(que, 'ul'))
ul_thread_list.append(ul)

for thread in ul_thread_list:
	thread.start()

for thread in ul_thread_list:
	thread.join()

while not que.empty():
	result.extend(que.get())

# structure of result list: timestamp;external_DLa;internal_DLa;Ping;external_DLs;external_ULa;internal_ULa;ping;external_Uls
# let's sort it in a meaningful way
avg_ping = (result[3] + result[7])/2
result.pop(7)
result.pop(3)
result.insert(1, avg_ping)
result.insert(4, result.pop(3))
diff_dl = result[2] - result[3]
result.insert(4, diff_dl)
result.insert(7, result.pop(8))
diff_ul = result[6] - result[7]
result.insert(8,diff_ul)
# structure result list: timestamp;avg_ping;external_DLa;external_DLs;external_DLo;internal_DLa;external_ULa;external_ULs;external_ULo;internal_ULa

# lets write the results to a file:
with open(filename,'a') as fout:
	writer = csv.writer(fout, delimiter = ";")
	writer.writerow(result)

os.system("python3 " + os.getcwd() + "/visualisation.py") # and start the visualisation script to generate the html file
