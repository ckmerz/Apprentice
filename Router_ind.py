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

######==AGLT2RTR==######
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
	
aglt2rtrpath = os.environ["aglt2rtr"]
if os.path.isdir(aglt2rtrpath):
	print("Path exists: ", aglt2rtrpath)
else:
	print("Path does not exist")

aglt2rtrls = os.environ["rtrls"]
if os.path.isdir(aglt2rtrls):
	print("Path exists: ", aglt2rtrls)
else:
	print("Path does not exist")

aglt2rtrpp = os.environ["rtrpp"]
if os.path.isdir(aglt2rtrpp):
	print("Path exists: ", aglt2rtrpp)
else:
	print("Path does not exist")

#subprocesses bash-python
first = subprocess.Popen(['/bin/echo', str(start_final), str(end_final), str(aglt2rtrls)], stdout=subprocess.PIPE)
second = subprocess.Popen(['bash', 'router_livestatus.sh', '{}'.format(start_final), '{}'.format(end_final), '{}'.format(aglt2rtrls)], stdin=first.stdout)
first.stdout.close()
output = second.communicate()[0]
first.wait()

third = subprocess.Popen(['/bin/echo', str(aglt2rtrls)], stdout=subprocess.PIPE)
fourth = subprocess.Popen(['bash', 'removechar.sh', '{}'.format(aglt2rtrls)], stdin=third.stdout)
third.stdout.close()
output1 = fourth.communicate()[0]
third.wait()

#save metrics to min, max, mean, std
data = pd.read_csv(os.path.join(aglt2rtrls,'livestatus_pp.txt'), header=None)
data.columns = ['Start_Time', 'End_Time', 'Frequency','D1','D2','D3','D4','D5']
data = data.drop(['Start_Time', 'End_Time', 'Frequency'], axis=1)

data_in = data[data.index % 2 == 0].copy(deep=True)
data_out = data[data.index % 2 == 1].copy(deep=True)

def preprocess_df(dfs, service):
	service = str(service)
	dfs.loc[:,"min"] = dfs.min(axis=1)
	dfs.loc[:,"max"] = dfs.max(axis=1)
	dfs.loc[:,"mean"] = dfs.mean(axis=1)
	dfs.loc[:,"std"] = dfs.std(axis=1)
	dfs = dfs.drop(['D1', 'D2', 'D3', 'D4','D5'], axis=1)
	dfs = dfs.T
	dfs.columns = ['rtr-1-eth-1-51', 'rtr-1-eth-1-52', 'rtr-2-eth-1-51', 'rtr-2-eth-1-52']
	#Tried 1/51, for some reason broke it lmao
	for col in dfs.columns:
		dfs[col].to_csv(os.path.join(aglt2rtrpp,'AGLT2RTR_{}_{}.csv'.format(service, col)), header=['srv']) #index=True
		
preprocess_df(data_in, "Input")
preprocess_df(data_out, "Output")