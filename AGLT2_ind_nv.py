#!/usr/bin/env python

import json
import requests
import os
import time
import datetime
import pandas as pd
import numpy as np
from Timing import roundups, rounddos
from requests.exceptions import Timeout
import subprocess
from multiprocessing import Process 


current = datetime.datetime.now()
current_5 = current - datetime.timedelta(minutes=5)
start = rounddos(current_5)
start_final = time.mktime(start.timetuple())
start_final = int(start_final)
end = rounddos(current)
end_final = time.mktime(end.timetuple())
end_final = int(end_final)

######==CHECK 1==######
print("start orig: ", current_5, " ", "start rounded: ", start, " ", "start unix: ", start_final)
print("end orig: ", current, " ", "end rounded: ", end, " ", "end unix: ", end_final)

timepath = os.environ["time"]
#timepath = os.environ['timepath'] = 'time'

if os.path.isdir(timepath):
	print("Path exists: ", timepath)
else: 
	print("Path does not exist")

with open(os.path.join(timepath, "Timing.txt"), "w" ) as f:
	f.write(str(start_final))
	f.write("\n")
	f.write(str(end_final))
	

checkmkpath = os.environ["checkmkls"]
if os.path.isdir(checkmkpath):
	print("Path exists: ", checkmkpath)
else:
	print("Path does not exist")
	
aglt2path = os.environ["aglt2"]
if os.path.isdir(aglt2path):
	print("Path exists: ", aglt2path)
else:
	print("Path does not exist")
	
pppath = os.environ["pp"]
if os.path.isdir(pppath):
	print("Path exists: ", pppath)
else:
	print("Path does not exist")
	
#subprocesses bash-python
first = subprocess.Popen(['/bin/echo', str(start_final), str(end_final), str(checkmkpath)], stdout=subprocess.PIPE)
second = subprocess.Popen(['bash', 'newlivestatus.sh', '{}'.format(start_final), '{}'.format(end_final), '{}'.format(checkmkpath)], stdin=first.stdout)
first.stdout.close()
output = second.communicate()[0]
first.wait()

third = subprocess.Popen(['/bin/echo', str(checkmkpath)], stdout=subprocess.PIPE)
fourth = subprocess.Popen(['bash', 'removechar.sh', '{}'.format(checkmkpath)], stdin=third.stdout)
third.stdout.close()
output1 = fourth.communicate()[0]
third.wait()

#save metrics to min, max, mean, std
data = pd.read_csv(os.path.join(checkmkpath,'livestatus_pp.txt'), header=None)
data.columns = ['Start_Time', 'End_Time', 'Frequency','D1','D2','D3','D4','D5']
data = data.drop(['Start_Time', 'End_Time', 'Frequency'], axis=1)

data_load = data[data.index % 4 == 0].copy(deep=True)
data_util = data[data.index % 4 == 1].copy(deep=True)
data_DIO = data[data.index % 4 == 2].copy(deep=True)
data_mem = data[data.index % 4 == 3].copy(deep=True)

cols = data_mem.columns
data_mem[cols] = data_mem[cols] * (1.25e-10)

def preprocess_df(dfs, service):
	service = str(service)
	dfs.loc[:,"min"] = dfs.min(axis=1)
	dfs.loc[:,"max"] = dfs.max(axis=1)
	dfs.loc[:,"mean"] = dfs.mean(axis=1)
	dfs.loc[:,"std"] = dfs.std(axis=1)
	dfs = dfs.drop(['D1', 'D2', 'D3', 'D4','D5'], axis=1)
	dfs = dfs.T
	dfs.columns = ['umfs06', 'umfs20', 'umfs23', 'umfs26', 'umfs09', 'umfs16', 'umfs21', 'umfs24', 'umfs27', 'umfs11', 'umfs19', 'umfs22', 'umfs25', 'umfs28', 'umfs29', 'umfs30', 'umfs31', 'umfs32', 'umfs33', 'umfs34']
	for col in dfs.columns:
		dfs[col].to_csv(os.path.join(pppath,'AGLT2_{}_{}.csv'.format(service, col)), header=['srv']) #index=True
		
preprocess_df(data_load, "CPU_load")
preprocess_df(data_util, "CPU_utilization")
preprocess_df(data_DIO, "Disk_IO_SUMMARY")
preprocess_df(data_mem, "Memory")
