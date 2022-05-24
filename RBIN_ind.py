#!/usr/bin/env python  
import csv
import json 
import requests 
import io 
import os 
import time  
import datetime 
import pandas as pd   
import numpy as np
from Timing import roundups, rounddos
from requests.exceptions import Timeout

current = datetime.datetime.now()  
current_5 = current - datetime.timedelta(minutes=5) 
start = rounddos(current_5)
start_final = time.mktime(start.timetuple()) 
end = rounddos(current) 
end_final = time.mktime(end.timetuple()) 

######==CHECK 1==###### 
#print("start orig: ", current_5, " ", "start rounded: ", start, " ", "start unix: ", start_final)
#print("end orig: ", current, " ", "end rounded: ", end, " ", "end unix: ", end_final)

#end_unix, end_datetime = Round(current) 
#start_unix, start_datetime = Round(current_5) 

url = "http://capm-da-asb.umnet.umich.edu:8581/odata/api/interfaces" 
#e.g 10s after 10 we want start: 9:55 and end, 10:00 
hosts = ['ae5', 'ae6', 'et-8/2/1']
#hosts = ['et-8/0/0','et-4/3/0', 'et-8/2/0']
#hosts = ['et-8/0/0', 'et-4/3/0']
#rbinpath = os.environ["rbin"]

#if os.path.isdir(rbinpath):
#	print("Path exists: ", rbinpath)
#else: 
#	print("Path does not exist")

for index, line in enumerate(hosts):
	print("===line===", line)
	querystring = {"resolution":"RATE","starttime":"{}".format(int(start_final)),"endtime":"{}".format(int(end_final)),"$expand":"portmfs","$select":"ID,portmfs/Timestamp,portmfs/im_BitsIn,portmfs/im_BitsOut,portmfs/im_BitsPerSecondIn,portmfs/im_BitsPerSecondOut,portmfs/im_UtilizationIn,portmfs/im_UtilizationOut","$filter":"((tolower(device/Name) eq tolower('r-bin-seb.umnet.umich.edu')) and (tolower(Name) eq tolower('{}')))".format(line)}
	payload = ""
	headers = {'cookie': "JSESSIONID=p0pnitc0u19atbaqu91ajkov", 'Authorization': "Basic c3BlY3RwZDozckJAZSFAbiE="}
	if line == 'et-8/2/0':
		time.sleep(240)
	else: 
		time.sleep(1)
	#time.sleep(10)
	try:
		response = requests.request("GET", url, data=payload, headers=headers, params=querystring, timeout=60)
	except Timeout:
		print("The request timed out")
	else: 
		print("The request is good")
	todos = response.text
	print(todos)
	#time.sleep(90)
	'''
	df = pd.read_csv(io.StringIO(todos))
	starttime = df["portmfs/Timestamp"].iloc[[0]]
	endtime = df["portmfs/Timestamp"].iloc[[-1]]
	df["portmfs/Timestamp"] = pd.to_datetime(df["portmfs/Timestamp"],unit='s')
	cols = df.columns.drop(['ID','portmfs/Timestamp','portmfs/im_UtilizationIn','portmfs/im_UtilizationOut'])  
	df[cols] = df[cols]* (1.25e-10) #bits to Gigabyte
	df = df.rename(columns={"portmfs/Timestamp": "Timestamp", "portmfs/im_BitsIn": "GBIn", "portmfs/im_BitsOut":"GBOut", "portmfs/im_BitsPerSecondIn":"GBpsIn", "portmfs/im_BitsPerSecondOut":"GBpsOut", "portmfs/im_UtilizationIn":"UtilIn", "portmfs/im_UtilizationOut":"UtilOut"})
	#df = df.drop(['ID','Timestamp'], axis=1)
	#df = df.T
	#print(df)
	
	metadata = ['GBIn', 'GBOut', 'GBpsIn', 'GBpsOut', 'UtilIn', 'UtilOut']

	def tocsv(var):
		var = str(var)
		data = [df["{}".format(var)]]
		header = ["{}".format(var)]
		newdf = pd.concat(data, axis=1, keys=header)
		newdf = newdf.T
		print("==var==", var)
		print(newdf)
		#newdf = newdf.to_csv(os.path.join(rbinpath,"RBIN_{}_{}.csv".format(var, index)), index=True)
		#checkpath = os.path.join(rbinpath,"RBIN_{}_{}.csv".format(var,index))
		#if os.path.exists(checkpath):
		#	print("Path and file exists", checkpath)
		#else:
		#	print("Path and file does not exist")
		#print("datadrame created for {}".format(var))
		return df

	for meta in range(len(metadata)):
		tocsv("{}".format(metadata[meta]))
	'''	
