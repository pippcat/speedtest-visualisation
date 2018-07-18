#!/usr/bin/env python3

import queue
import threading
import psutil
import csv
import time
import os

from datetime import datetime

result = []
filename = "data.csv"

def bw(direction):
	interval = 2 # measurement interval
	time.sleep(10) # to make sure speedtest already started
	before = psutil.net_io_counters(pernic=True)
	eth0_before = before["eth0"]
	eth1_before = before["eth1"]
	eth0_rv_before = eth0_before[1]
	eth0_tx_before = eth0_before[0]
	eth1_rv_before = eth1_before[1]
	eth1_tx_before = eth1_before[0]

	time.sleep(interval)

	after = psutil.net_io_counters(pernic=True)
	eth0_after = after["eth0"]
	eth1_after = after["eth1"]
	eth0_rv_after = eth0_after[1]
	eth0_tx_after = eth0_after[0]
	eth1_rv_after = eth1_after[1]
	eth1_tx_after = eth1_after[0]
	if direction=="dl":
		eth0_rv_per_sec = (eth0_rv_after - eth0_rv_before) / interval / 1000000 * 8
		eth1_rv_per_sec = (eth1_rv_after - eth1_rv_before) / interval / 1000000 * 8
		print("BW DL test done. eth0_rv_per_sec = " + str(eth0_rv_per_sec) + "; eth1_rv_per_sec = " + str(eth1_rv_per_sec))
		return [eth0_rv_per_sec, eth1_rv_per_sec]
	elif direction=="ul":
		eth0_tx_per_sec = (eth0_tx_after - eth0_tx_before) / interval / 1000000 * 8
		eth1_tx_per_sec = (eth1_tx_after - eth1_tx_before) / interval / 1000000 * 8
		print("BW UL test done. eth0_tx_per_sec = " + str(eth0_tx_per_sec) + "; eth1_tx_per_sec = " + str(eth1_tx_per_sec))
		return [eth0_tx_per_sec, eth1_tx_per_sec]

def speedtest(direction):
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
		print("Speedtest DL test done. ping = " + str(results_dict['ping']) + "ms; eth0 DL speed = " + str(results_dict['download']/1000000))
		return [results_dict['ping'], results_dict['download']/1000000]
	elif direction=="ul":
		print("Speedtest UL test done. ping = " + str(results_dict['ping']) + "ms; eth0 UL speed = " + str(results_dict['upload']/1000000))
		return [results_dict['ping'], results_dict['upload']/1000000]

que = queue.Queue()
dl_thread_list = list()
ul_thread_list = list()
dl = threading.Thread(target=lambda q, arg1: q.put(speedtest(arg1)), args=(que, 'dl'))
dl_thread_list.append(dl)
dl = threading.Thread(target=lambda q, arg1: q.put(bw(arg1)), args=(que, 'dl'))
dl_thread_list.append(dl)

for thread in dl_thread_list:
	thread.start()

result.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

for thread in dl_thread_list:
	thread.join()

while not que.empty():
	result.extend(que.get())

t = threading.Thread(target=lambda q, arg1: q.put(speedtest(arg1)), args=(que, 'ul'))
ul_thread_list.append(t)
t = threading.Thread(target=lambda q, arg1: q.put(bw(arg1)), args=(que, 'ul'))
ul_thread_list.append(t)

for thread in ul_thread_list:
	thread.start()

for thread in ul_thread_list:
	thread.join()

while not que.empty():
	result.extend(que.get())

#print("Result :" + str(result))
#structure now: timestamp;eth0_DLa;eth1_DLa;Ping;eth0_DLs;eth0_ULa;eth1_ULa;ping;eth0_Uls
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
#structure now: timestamp;avg_ping;eth0_DLa;eth0_DLs;eth0_DLo;eth1_DLa;eth0_ULa;eth0_ULs;eth0_ULo;eth1_ULa

#print("Result :" + str(result))
with open(filename,'a') as fout:
	writer = csv.writer(fout, delimiter = ";")
	writer.writerow(result)

os.system("python3 /home/tommy/speedtest-visualisation/visualisation.py")
