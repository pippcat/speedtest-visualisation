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
	time.sleep(8)
	if direction=="dl":
		rv_before = psutil.net_io_counters().bytes_recv
	elif direction=="ul":
		tx_before = psutil.net_io_counters().bytes_sent
	time.sleep(2)
	if direction=="dl":
		rv_after = psutil.net_io_counters().bytes_recv
		rv_per_sec = (rv_after - rv_before) / 2 / 1000000 * 8
		return rv_per_sec
	elif direction=="ul":
		tx_after = psutil.net_io_counters().bytes_sent
		tx_per_sec = (tx_after - tx_before) / 2 / 1000000 * 8
		return tx_per_sec

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
		return results_dict['download']/1000000
	elif direction=="ul":
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
	result.append(que.get())
diff = result[1] - result[2]
result.append(diff)

t = threading.Thread(target=lambda q, arg1: q.put(speedtest(arg1)), args=(que, 'ul'))
ul_thread_list.append(t)
t = threading.Thread(target=lambda q, arg1: q.put(bw(arg1)), args=(que, 'ul'))
ul_thread_list.append(t)

for thread in ul_thread_list:
	thread.start()

for thread in ul_thread_list:
	thread.join()

#while not que.empty():
result.append(que.get())
result.extend(que.get())
#print(str(result))
diff = result[4] - result[6]
result.append(diff)
#structure now: timestamp;DLa;DLs;DLd;ULa;Ping;ULs;ULd
result.insert(1, result.pop(5))
#structure now: timestamp;DLa;DLs;DLd;ULa;Ping;ULs;ULd

print("Result :" + str(result))

with open(filename,'a') as fout:
	writer = csv.writer(fout, delimiter = ";")
	writer.writerow(result)

os.system("python3 speedtest-visualisation.py")
