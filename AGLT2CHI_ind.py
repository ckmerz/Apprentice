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
import re 

current = datetime.datetime.now()
current_5 = current - datetime.timedelta(minutes=5) 
start = rounddos(current_5)
start_final = time.mktime(start.timetuple())   
end = rounddos(current)
end_final = time.mktime(end.timetuple())
#end_unix, end_datetime = Round(current) 
#start_unix, start_datetime = Round(current_5)  

######==CHECK 1==######  
#print("start orig: ", current_5, " ", "start rounded: ", start, " ", "start unix: ", start_final)   
#print("end orig: ", current, " ", "end rounded: ", end, " ", "end unix: ", end_final)  

url = "https://grafana.omnipop.btaa.org/grafana/api/datasources/proxy/115/query.cgi"

identifier = ['620d46c684eff80106ffc4b5769f77e9f658cc7c3ee3cd847261da09570167f3', '696e977330667f44c13ffe5364446c96a2fa4cc9137b9e5ddbd23605bf489e12', 'fa5373adef061fa051ef458a8e028a84749385edb16955537eac43712b6ef72b', '939820268eaf905fae19a951a9bd73af2834017d0d2744229d71608b47afdf1c', 'd3947c64aa4ebd202cff06fb9c5e6badf51296db72ab3ba8ff01f35811d423ae', '1dd502cdcfac422ff031a6f097ef8385c7b4078b4a4b19081bb39c0dd86ddae7']
#identifier = ['620d46c684eff80106ffc4b5769f77e9f658cc7c3ee3cd847261da09570167f3']
#new identifiers  
#1. sw2.star.omnipop.btaa.org - et-1/0/1 - University of Michigan 100G | BTAA-STAR-STAR-100GE-1620  
#620d46c684eff80106ffc4b5769f77e9f658cc7c3ee3cd847261da09570167f3     
#2. sw2.star.omnipop.btaa.org - et-0/0/0 - L2 BB sw2.star to sw2.600WChicag et-0/0/0 200G LAG | BTAA-600WCHICAG-STAR-100GE-01578 
#696e977330667f44c13ffe5364446c96a2fa4cc9137b9e5ddbd23605bf489e12 
#3. sw2.star.omnipop.btaa.org - et-1/0/0 - L2 BB sw2.star to sw2.600WChicag et-0/0/2 200G LAG | BTAA-600WCHICAG-STAR-100GE-01579
#fa5373adef061fa051ef458a8e028a84749385edb16955537eac43712b6ef72b
#4. sw2.star.omnipop.btaa.org - et-0/1/0 - ESnet 100G | BTAA-STAR-STAR-100GE-1623#939820268eaf905fae19a951a9bd73af2834017d0d2744229d71608b47afdf1c
#5 sw2.600wchicag.omnipop.btaa.org - et-0/1/0 - ESnet 100GE 1of2 for LAG | BTAA-600WCHICAG-600WCHICAG-100GE-02273
#d3947c64aa4ebd202cff06fb9c5e6badf51296db72ab3ba8ff01f35811d423ae 
#6. sw2.600wchicag.omnipop.btaa.org - et-1/0/2 - ESnet 100GE 2of2 for LAG | BTAA-600WCHICAG-600WCHICAG-100GE-02274
#1dd502cdcfac422ff031a6f097ef8385c7b4078b4a4b19081bb39c0dd86ddae7

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
	df_input = df_input.resample("5T").agg(['min','max','mean', 'std'], axis="columns").round(5)
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
	df_output = df_output.resample("5T").agg(['min','max','mean', 'std'], axis="columns").round(5)
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
