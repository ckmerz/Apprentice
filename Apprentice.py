#!/usr/bin/env python
"""First version of the full script. 
Started w/ nv.py as base, added parts from CHI, RBIN, extract, dict_maker, & Timing.
Not adding removechar.sh & newlivestatus.sh because they're shell scripts!"""
import json
import requests
import os
import time
import datetime as dt
from datetime import datetime, timedelta #from extract & Timing
import pandas as pd
import numpy as np
from requests.exceptions import Timeout
import subprocess 
"""Needed ^ cuz not adding the scripts this effects. 
They're shell scripts & don't play nice in the python env"""
from multiprocessing import Process 
import re #from CHI
import csv #from RBIN
import io #RBIN
import matplotlib.dates as md #from extract
import matplotlib.pyplot as plt #extract
import itertools #ext
import glob #ext

######==Timing.py==######
#Added instead of importing roundups & rounddos 
def roundups(dt):
    roundup = dt + (datetime.min - dt) % timedelta(minutes=5)
    return roundup

def rounddos(dt):
    rounddo = dt - (dt - datetime.min) % timedelta(minutes=5)
    return rounddo 
######==Timing.py==######

current = datetime.datetime.now()
current_5 = current - datetime.timedelta(minutes=5)
start = rounddos(current_5)
start_final = time.mktime(start.timetuple())
start_final = int(start_final)
end = rounddos(current)
end_final = time.mktime(end.timetuple())
end_final = int(end_final)
"""end_unix, end_datetime = Round(current) 
start_unix, start_datetime = Round(current_5) 
Both ^ commented out in CHI. Next 2 'print' lines in CHI & nv.py, but nv.py seems to work
fine w/ out the unix lines so I don't think they're needed at all. Kept just in case."""

######==CHECK 1==###### nv.py base
print("start orig: ", current_5, " ", "start rounded: ", start, " ", "start unix: ", start_final)
print("end orig: ", current, " ", "end rounded: ", end, " ", "end unix: ", end_final)

timepath = os.environ["time"]
if os.path.isdir(timepath):
	print("Path exists: ", timepath)
else: 
	print("Path does not exist")

with open(os.path.join(timepath, "Timing.txt"), "w" ) as f:
	f.write(str(start_final))
	f.write("\n")
	f.write(str(end_final))
	lines = f.read() #added from very similar section in dict_maker. 
	#Needed 4 'lines' var there
	
checkmkpath = os.environ["checkmkls"]
if os.path.isdir(checkmkpath):
	print("Path exists: ", checkmkpath)
else:
	print("Path does not exist")
	
"""aglt2path = os.environ["aglt2"]
if os.path.isdir(aglt2path):
	print("Path exists: ", aglt2path)
else:
	print("Path does not exist")
Don't need ^, exact same chunk defined in extract_dict section 
"""	
pppath = os.environ["pp"]
if os.path.isdir(pppath):
	print("Path exists: ", pppath)
else:
	print("Path does not exist")
#Also defined in extract_dict, but needed here in "def preprocess_df" section a few chunks down
	
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
	dfs.columns = ['umfs06', 'umfs09', 'umfs11', 'umfs16', 'umfs19', 'umfs20', 'umfs21', 'umfs22', 'umfs23', 'umfs24', 'umfs25', 'umfs26', 'umfs27', 'umfs28', 'umfs29', 'umfs30', 'umfs31', 'umfs32', 'umfs33', 'umfs34']
	for col in dfs.columns:
		dfs[col].to_csv(os.path.join(pppath,'AGLT2_{}_{}.csv'.format(service, col)), header=['srv']) #index=True
		
preprocess_df(data_load, "CPU_load")
preprocess_df(data_util, "CPU_utilization")
preprocess_df(data_DIO, "Disk_IO_SUMMARY")
preprocess_df(data_mem, "Memory")


######==Chicago==###### only the unique parts, there's overlap w/ nv.py
url = "https://grafana.omnipop.btaa.org/grafana/api/datasources/proxy/115/query.cgi"
identifier = ['620d46c684eff80106ffc4b5769f77e9f658cc7c3ee3cd847261da09570167f3', '696e977330667f44c13ffe5364446c96a2fa4cc9137b9e5ddbd23605bf489e12', 'fa5373adef061fa051ef458a8e028a84749385edb16955537eac43712b6ef72b', '939820268eaf905fae19a951a9bd73af2834017d0d2744229d71608b47afdf1c', 'd3947c64aa4ebd202cff06fb9c5e6badf51296db72ab3ba8ff01f35811d423ae', '1dd502cdcfac422ff031a6f097ef8385c7b4078b4a4b19081bb39c0dd86ddae7']

aglt2chipath = os.environ["aglt2chi"]

if os.path.isdir(aglt2chipath):
	print("Path exists: ", aglt2chipath)
else: 
	print("Path does not exist")

for index, line in enumerate(identifier):
	print("===line===", line)
	query = "method=query;query=get%20intf%2C%20node%2C%20description%2C%20aggregate(values.input%2C%2060%2C%20average)%2C%20aggregate(values.output%2C%2060%2C%20average)%20between%20({}%2C%20{})%20by%20intf%2Cnode%20from%20interface%20where%20((identifier%20%3D%20%22{}%22))%20ordered%20by%20node".format(int(start_final),int(end_final),line)
	try:
		response = requests.request("POST", url,data=query, timeout=60)
	except Timeout:
		print("Timed Out") 
	else:
		print("Request is good")

	todos = json.loads(response.text)
	todos == response.json() 
	#time.sleep(300)
        #print(todos)
	df = pd.DataFrame(todos)
	#print(df)
	results = df["results"][0] 
	df_results = pd.DataFrame(data=results) 
	#print(df_results.columns)
	df_results.columns = ['input', 'intf', 'description', 'node', 'output']
	intf = df_results['intf'][0]
	node = df_results['node'][0]
	print(intf)
	print(node)
	row, col = df_results.shape
	time = []
	inputval = []  
	outputval = []

	#print(df_results["input"][0][1], df_results["output"][0][1])
	#print(df_results["input"][0])
	for i in range(row): 
		time.append(df_results["input"][i][0])  
		inputval.append(df_results["input"][i][1])
		outputval.append(df_results["output"][i][1]) 
		
	#inputval.insert(len(inputval), 0)
	#outputval.insert(len(outputval), 0)
	time.insert(len(time), time[len(time)-1]+60) 
	tuple_in = list(zip(time, inputval))
	tuple_out = list(zip(time, outputval))
	tuples = list(zip(time, inputval, outputval)) 
	#print(tuples)
	#Do warning, count of NANs 

	df_input = pd.DataFrame(data = tuple_in,columns=['Timestamp','Input'])
	#df_input["Input"] = df_input["Input"].replace(np.nan,0)
	df_input["Timestamp"] = pd.to_datetime(df_input["Timestamp"],unit='s')
	df_input = df_input.set_index(["Timestamp"])
	df_input = df_input.resample("5T").agg(['min','max','mean','std'], axis="columns").round(5)
	cols = df_input.columns
	df_input[cols] = df_input[cols] *(1.25e-10)
	df_input = df_input[:1]
	df_input = df_input.reset_index()
	df_input = df_input.drop('Timestamp', axis=1)
	df_input = df_input.T
	print(df_input)
	df_input = df_input.to_csv(os.path.join(aglt2chipath, "AGLT2_CHI_input_{}.csv".format(index)), index=True)
	check_input = os.path.join(aglt2chipath, "AGLT2_CHI_input_{}.csv".format(index))
	if os.path.exists(check_input):
		print("Path and file exists", check_input)
	else:
		print("Path and file does not exist")

	#print(df_input)
	#df_input = df_input.to_csv("../Output/Raw/AGLT2_CHI/AGLT2_CHI_input_{}.csv".format(index), index=True)	

	df_output = pd.DataFrame(data = tuple_out,columns=['Timestamp','Output'])
	#df_output["Output"] = df_output["Output"].replace(np.nan,0)
	df_output["Timestamp"] = pd.to_datetime(df_output["Timestamp"],unit='s')
	df_output = df_output.set_index(["Timestamp"])
	df_output = df_output.resample("5T").agg(['min','max','mean','std'], axis="columns").round(5)
	cols = df_output.columns
	df_output[cols] = df_output[cols] *(1.25e-10)
	df_output = df_output[:1]
	df_output = df_output.reset_index()
	df_output = df_output.drop('Timestamp', axis=1)
	df_output = df_output.T
	print(df_output)
	df_output = df_output.to_csv(os.path.join(aglt2chipath, "AGLT2_CHI_output_{}.csv".format(index)), index=True)
	check_output = os.path.join(aglt2chipath, "AGLT2_CHI_output_{}.csv".format(index))
	if os.path.exists(check_output):
		print("Path and file exists", check_output)
	else:
		print("Path and file does not exist")

	#print(df_output)
	#df_output = df_output.to_csv("../Output/Raw/AGLT2_CHI/AGLT2_CHI_output_{}.csv".format(index), index=True)
	
	#Commented out all of the CHI section for now 

######==RBIN==###### only unique parts

url = "http://capm-da-asb.umnet.umich.edu:8581/odata/api/interfaces" 
hosts = ['ae5', 'ae6', 'et-8/2/1']
#For the 4 router connections: hosts = ['1/51', '1/52']
#There's 2 of each of these for the routers, how to specify this in the code? 


#hosts = ['et-4/3/0', 'et-8/0/0', 'et-8/2/0']
#Wrong ports ^, this is the old list

"""if os.path.isdir(rbinpath):
	print("Path exists: ", rbinpath)
else: 
	print("Path does not exist")
Chunk ^ commented out in CHI because it's defined in extract_dict instead"""

for index, line in enumerate(hosts):
	print("===line===", line)
	querystring = {"resolution":"RATE","starttime":"{}".format(int(start_final)),"endtime":"{}".format(int(end_final)),"$expand":"portmfs","$select":"ID,portmfs/Timestamp,portmfs/im_BitsIn,portmfs/im_BitsOut,portmfs/im_BitsPerSecondIn,portmfs/im_BitsPerSecondOut,portmfs/im_UtilizationIn,portmfs/im_UtilizationOut","$filter":"((tolower(device/Name) eq tolower('r-bin-seb.umnet.umich.edu')) and (tolower(Name) eq tolower('{}')))".format(line)}
	payload = ""
	headers = {'cookie': "JSESSIONID=p0pnitc0u19atbaqu91ajkov", 'Authorization': "Basic c3BlY3RwZDozckJAZSFAbiE="}
	"""if line == 'et-8/2/0':
		time.sleep(240)
	else: 
		time.sleep(1)
	Delay not needed for the final, not checking 8/2/0 anymore"""

	try:
		response = requests.request("GET", url, data=payload, headers=headers, params=querystring, timeout=60)
	except Timeout:
		print("The request timed out")
	else: 
		print("The request is good")
	todos = response.text
	print(todos)

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
	#Why commented out in RBIN? 

######==extract_dict==###### only unique parts. 
#Defines AGLT2, AGLT2CHI, RBIN and  in the for loops of the dict_maker section 
def AGLT2(metadata):
	metadata = str(metadata)
	#outpath = "/NetBASILISK/IndEnv/newAGLT2/EnvironmentMonitoring/Scripts/newAGLT2/Output/Output_20220509_1707/Raw/AGLT2/pp"
	#outpath = "../Output/Raw/AGLT2"
	aglt2path = os.environ["aglt2"]
	if os.path.isdir(aglt2path):
		print("Path exists: ", aglt2path)
	else:
		print("Path does not exist")
	
	"""pppath = os.environ["pp"]
	if os.path.isdir(pppath):
		print("Path exists: ", pppath)
	else:
		print("Path does not exist")
	Not needed because defined earlier in nv.py section 
	"""	
	
	csvfiles = glob.glob(os.path.join(pppath, 'AGLT2_{}_*.csv'.format(metadata)))
	csvfiles = sorted(csvfiles)
	#print("Check the order of the files")
	#print(csvfiles)
	dataframes = []
	for files in csvfiles: 
		#print(files)
		df = pd.read_csv(files)
		dataframes.append(df)

	result = pd.concat(dataframes, ignore_index=True)
	DATA = pd.DataFrame(data = result)
	DATA = DATA.round(4)
	#print(DATA)
	df_min = DATA[DATA.index % 4 == 0].copy(deep=True)
	df_max = DATA[DATA.index % 4 == 1].copy(deep=True)
	df_mean = DATA[DATA.index % 4 == 2].copy(deep=True)
	df_std = DATA[DATA.index % 4 == 3].copy(deep=True)
	
	def transpose(dataframe):
		df = dataframe.T
		df.columns = ['umfs06', 'umfs09', 'umfs11', 'umfs16', 'umfs19', 'umfs20', 'umfs21', 'umfs22', 'umfs23', 'umfs24', 'umfs25', 'umfs26', 'umfs27', 'umfs28', 'umfs29', 'umfs30', 'umfs31', 'umfs32', 'umfs33', 'umfs34']
		df.drop(['Unnamed: 0'], axis = 0, inplace=True)
		#print(df.columns)
		df = dataframe.drop(['Unnamed: 0'], axis = 1)
		df['Servers'] = ['umfs06', 'umfs09', 'umfs11', 'umfs16', 'umfs19', 'umfs20', 'umfs21', 'umfs22', 'umfs23', 'umfs24', 'umfs25', 'umfs26', 'umfs27', 'umfs28', 'umfs29', 'umfs30', 'umfs31', 'umfs32', 'umfs33', 'umfs34']
		df = pd.Series(df['srv'].values,index=df.Servers).to_dict()
		return df
	dfmin = transpose(df_min)
	dfmax = transpose(df_max)
	dfmean = transpose(df_mean)
	dfstd = transpose(df_std)
	#print(dfmin)
	return dfmin, dfmax, dfmean, dfstd

#AGLT2_CHI_0.csv 
def AGLT2CHI(metadata):
	metadata = str(metadata)
	#outpath = "../Output/Raw/AGLT2_CHI"
	aglt2chipath = os.environ["aglt2chi"]
	if os.path.isdir(aglt2chipath):
		print("Path exists: ", aglt2chipath)
	else:
		print("Path does not exist")
	csvfiles = glob.glob(os.path.join(aglt2chipath, 'AGLT2_CHI_{}_*.csv'.format(metadata))) 	
	csvfiles = sorted(csvfiles)
	#print("Check the order of the files") 
	#print(csvfiles)  
	dataframes = []
	for files in csvfiles:
		df = pd.read_csv(files)
		dataframes.append(df)
	
	result = pd.concat(dataframes, ignore_index=True)
	DATA = pd.DataFrame(data = result)
	DATA = DATA.round(4)
	#print(DATA)

	df_min = DATA[DATA.index % 4 == 0].copy(deep=True)
	df_max = DATA[DATA.index % 4 == 1].copy(deep=True)
	df_mean = DATA[DATA.index % 4 == 2].copy(deep=True)
	df_std = DATA[DATA.index % 4 == 3].copy(deep=True)
	
	#dfs = [df_min, df_max, df_mean, df_std]

	#def transpose(index, dataframe):
	def transpose(dataframe):
		df = dataframe.T
		df.columns = ['ae5', 'ae6', 'et-8/2/1']
		#df.columns = ['et-1/0/1-star', 'et-0/0/0-star', 'et-1/0/0-star', 'et-0/1/0-star', 'et-0/1/0-600w','et-1/0/2-600w']
		#Old list ^ 
		df.drop(['Unnamed: 0', 'Unnamed: 1'], axis = 0, inplace=True)
		df = dataframe.drop(['Unnamed: 0', 'Unnamed: 1'], axis = 1)
		df['nodes'] = ['ae5', 'ae6', 'et-8/2/1']
		#df['nodes'] = ['et-1/0/1-star', 'et-0/0/0-star', 'et-1/0/0-star', 'et-0/1/0-star', 'et-0/1/0-600w','et-1/0/2-600w']
		#Old ^ 
		df = pd.Series(df['0'].values,index=df.nodes).to_dict()
		return df
		#print(df)
	
	#for index, df in enumerate(dfs):
	#	transpose(index,df)
	dfmin = transpose(df_min)
	dfmax = transpose(df_max)
	dfmean = transpose(df_mean)
	dfstd = transpose(df_std)
	return dfmin, dfmax, dfmean, dfstd

	
def RBIN(metadata):
	metadata = str(metadata)
	#outpath = "../Output/Raw/RBIN"
	rbinpath = os.environ["rbin"]
	if os.path.isdir(rbinpath):
		print("Path exists: ", rbinpath)
	else:
		print("Path does not exist")
	csvfiles = glob.glob(os.path.join(rbinpath, 'RBIN_{}_*.csv'.format(metadata)))
	csvfiles = sorted(csvfiles)
	#print("Check the order of the files")
	#print(csvfiles)
	dataframes = []
	for files in csvfiles:
		df = pd.read_csv(files)
		dataframes.append(df)

	result = pd.concat(dataframes, ignore_index=True)
	DATA = pd.DataFrame(data = result)
	DATA = DATA.round(4)
	#print(DATA)
	
	df = DATA.T
	df.columns = ['ae5', 'ae6', 'et-8/2/1']
	#df.columns = ['et-8/2/0','et-8/0/0', 'et-4/3/0']
	#df.columns = ['et-8/0/0', 'et-4/3/0']
	#Oldio ^
	df.drop(['Unnamed: 0'], axis = 0, inplace=True)
	df = DATA.drop(['Unnamed: 0'], axis = 1)
	df ['nodes'] = ['ae5', 'ae6', 'et-8/2/1']
	#df['nodes'] = ['et-8/0/0', 'et-4/3/0']
	#df['nodes'] = ['et-8/2/0','et-8/0/0', 'et-4/3/0']
	#Super old

	df = pd.Series(df['0'].values,index=df.nodes).to_dict()
	return df

def AGLT2RTR(metadata):
	metadata = str(metadata)
	aglt2rtrpath = os.environ["aglt2rtr"]
	#outpath = "../Output/Raw/routes/seperate the routers into 2 dirs after this?"
	if os.path.isdir(aglt2rtrpath):
		print("Path exists: ", aglt2rtrpath)
	else:
		print("Path does not exist")
	csvfiles = glob.glob(os.path.join(aglt2rtrpath, 'AGLT2RTR_{}_*.csv'.format(metadata)))
	csvfiles = sorted(csvfiles)
	dataframes = []
	for files in csvfiles:
		df = pd.read_csv(files)
		dataframes.append(df)
	result = pd.concat(dataframes, ignore_index=True)
	DATA = pd.DataFrame(data = result)
	DATA = DATA.round(4)	
	#df = DATA.T
	#df.columns = ['1/51', '1/52']
	#Not sure if this'll cover all 4 connections? 
	dfGb_in = DATA[DATA.index % 4 == 0].copy(deep=True)
	dfGb_out = DATA[DATA.index % 4 == 1].copy(deep=True)
	def transpose(dataframe):
		df = dataframe.T
		df.columns = ['aglt2-rtr-1', 'aglt2-rtr-2']
		df.drop(['Unnamed: 0'], axis = 0, inplace=True)
		df = dataframe.drop(['Unnamed: 0'], axis = 1)
		df['Routers'] = ['aglt2-rtr-1', 'aglt2-rtr-2']
		df = pd.Series(df['srv'].values,index=df.Routers).to_dict()
		return df
	dfmin = transpose(dfGb_in)
	dfmax = transpose(dfGb_out)
	return dfGb_in, dfGb_out

######==dict_maker==###### only unique parts
aglt2 = ['CPU_load', 'CPU_utilization', 'Disk_IO_SUMMARY', 'Memory']
aglt2chi = ['input', 'output']
rbin = ['GBIn', 'GBOut', 'GBpsIn', 'GBpsOut', 'UtilIn', 'UtilOut']
aglt2rtr = ['Interface Ethernet']
#rtr = ['Gb_in', 'Gb_out']
# ^ Making the data type from checkmk for the 4 router connections
"""Also, aglt2chi & rbin lines were commented out temporarily because I think 
they weren't done/working properly initially"""

aglt2_min = []
aglt2_max = []
aglt2_mean = []
aglt2_std = []

aglt2chi_min = []
aglt2chi_max = []
aglt2chi_mean = []
aglt2chi_std = []
rbin_metrics = []

aglt2rtr_Gb_in = []
aglt2rtr_Gb_out = []

#aglt2rtr_? = []
#rtr_in = []
#rtr_out = []
#Just a guess ^
#From https://um-omd.aglt2.org/atlas/check_mk/index.py?start_url=%2Fatlas%2Fcheck_mk%2Fview.py%3Fhost%3Daglt2-rtr-1%26service%3DInterface%2BEthernet1%252F51%26site%3Datlas%26view_name%3Dservice
#Data from site in raw form is in bytes, need to convert to mb

for i in range(len(aglt2)):
	print("====AGLT2====", aglt2[i])
	dfmin, dfmax, dfmean, dfstd = AGLT2("{}".format(aglt2[i]))
	aglt2_min.append(dfmin)
	aglt2_max.append(dfmax)
	aglt2_mean.append(dfmean)
	aglt2_std.append(dfstd)

for j in range(len(aglt2chi)):
	print("====AGLT2_CHI====", aglt2chi[j])
	dfmin, dfmax, dfmean, dfstd = AGLT2CHI("{}".format(aglt2chi[j]))
	aglt2chi_min.append(dfmin)
	aglt2chi_max.append(dfmax)
	aglt2chi_mean.append(dfmean)
	aglt2chi_std.append(dfstd)

for k in range(len(rbin)):
	print("====RBIN====", rbin[k])
	metrics = RBIN("{}".format(rbin[k]))
	rbin_metrics.append(metrics)

for m in range (len(aglt2rtr)):
	print("====AGLT2_routers====", aglt2rtr[m])
	dfGb_in, dfGb_out = AGLT2RTR("{}".format(aglt2rtr[m]))
	aglt2rtr.append(dfGb_in)
	aglt2rtr.append(dfGb_out)


"""timepath = os.environ["time"]
if os.path.isdir(timepath):
        print("Path exists: ", timepath)
else:
        print("Path does not exist")

with open(os.path.join(timepath, "Timing.txt") ) as f:
	lines = f.read()
Don't think I need this, almost exact same chunk exists in nv.py section 	
"""

startime = int(lines[0:10])
startime = datetime.datetime.utcfromtimestamp(startime).strftime('%Y-%m-%d %H:%M:%S')
endtime = int(lines[11:21])
endtime = datetime.datetime.utcfromtimestamp(endtime).strftime('%Y-%m-%d %H:%M:%S')

data = {
	"summary": {
		'Name': 'Environment Metrics'
		,
		'Start': startime #AGLT2_ind.start_final
		,
		'End': endtime #AGLT2_ind.end_final
	}, 
	"aglt2 dest":{
		'CPU Load Min': aglt2_min[0]
		,
		'CPU Load Max': aglt2_max[0]
		,
		'CPU Load Ave': aglt2_mean[0]
		, 
		'CPU Load Std': aglt2_std[0]
		,
		'CPU Utilization Min': aglt2_min[1]
		,
		'CPU Utilization Max': aglt2_max[1]
		,
		'CPU Utilization Ave': aglt2_mean[1]
		,
		'CPU Utilization Std': aglt2_std[1]
		,
		'Disk IO Min': aglt2_min[2]
		, 
		'Disk IO Max': aglt2_max[2]
		,
		'Disk IO Ave': aglt2_mean[2]
		, 
		'Disk IO Std': aglt2_std[2]
		, 
		'Memory Min': aglt2_min[3] 
		, 
		'Memory Max': aglt2_max[3]
		, 
		'Memory Ave': aglt2_mean[3]
		, 
		'Memory Std': aglt2_std[3]
	},
#}When I uncommented the next section, this bracket caused problems

#From here to the end of the list used to be commented out
	"paths":{
		"chic-aglt2":{
			'Input Min': aglt2chi_min[0] 
			,
			'Input Max': aglt2chi_max[0]
			,
			'Input Ave': aglt2chi_mean[0]
			,
			'Input Std': aglt2chi_std[0]
			,
			'Output Min': aglt2chi_min[1]
			,
			'Output Max': aglt2chi_max[1]
			,
			'Output Ave': aglt2chi_mean[1]
			,
			'Output Std': aglt2chi_std[1]
		},
		"rbin":{
			'GBIn': rbin_metrics[0]
			,
			'GBOut': rbin_metrics[1]
			,
			'GBpsIn': rbin_metrics[2]
			,
			'GBpsOut': rbin_metrics[3]
			,
			'UtilIn': rbin_metrics[4]
			,
			'UtilOut': rbin_metrics[5] 
		},
	},
	"routers":{ #Figure out what #s to use here! 
		"AGLT2-1":{
			'IntEthIn': dfGb_in[1]
			,
			'IntEthOut': dfGb_out[1]
		},
		"AGLT2-2":{
			'IntEthIn': dfGb_in[1]
			,
			'IntEthOut': dfGb_out[1]
		},
	},
}

date = os.environ["currentdate"]
dictpath = os.environ["dict"]
#print(data)

if os.path.isdir(dictpath):
        print("Path exists: ", dictpath)
else:
        print("Path does not exist")

with open(os.path.join(dictpath,'dict_{}.json'.format(date)), 'w') as json_file:
    json.dump(data, json_file, indent=4)

	