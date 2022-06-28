import json
import matplotlib.dates as md
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt
import time
from datetime import datetime
import itertools
import glob
import os

def AGLT2(metadata):
	metadata = str(metadata)
	aglt2path = os.environ["aglt2"]
	#outpath = "../Output/Raw/AGLT2/checkmk"
	checkmkpppath = os.environ["checkmkpp"]
	#outpath = "../Output/Raw/AGLT2/checkmk/pp" 

	#Checkmk path
	if os.path.isdir(aglt2path):
		print("Path exists: ", aglt2path)
	else:
		print("Path does not exist")
	
	#Checkmk/pp path
	if os.path.isdir(checkmkpppath):
		print("Path exists: ", checkmkpppath)
	else:
		print("Path does not exist")	
	
	csvfiles = glob.glob(os.path.join(checkmkpppath, 'AGLT2_{}_*.csv'.format(metadata)))
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
		'''
		df = dataframe.T
		df.columns = ['umfs06', 'umfs09', 'umfs11', 'umfs16', 'umfs19', 'umfs20', 'umfs21', 'umfs22', 'umfs23', 'umfs24', 'umfs25', 'umfs26', 'umfs27', 'umfs28']
		df.drop(['Unnamed: 0', 'Unnamed: 1'], axis = 0, inplace=True)
		#print(df.columns)
		df = dataframe.drop(['Unnamed: 0', 'Unnamed: 1'], axis = 1)
		df['Servers'] = ['umfs06', 'umfs09', 'umfs11', 'umfs16', 'umfs19', 'umfs20', 'umfs21', 'umfs22', 'umfs23', 'umfs24', 'umfs25', 'umfs26', 'umfs27', 'umfs28']
		df = pd.Series(df['0'].values,index=df.Servers).to_dict()
		return df
		#print(df)
		'''
	#for index, df in enumerate(dfs):
	#	transpose(index, df)
	#	dfmin, dfmax, dfmean, dfstd = transpose(index,df)
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

	df_chimin = DATA[DATA.index % 4 == 0].copy(deep=True)
	df_chimax = DATA[DATA.index % 4 == 1].copy(deep=True)
	df_chimean = DATA[DATA.index % 4 == 2].copy(deep=True)
	df_chistd = DATA[DATA.index % 4 == 3].copy(deep=True)

	#df_min = DATA[DATA.index % 4 == 0].copy(deep=True)
	#df_max = DATA[DATA.index % 4 == 1].copy(deep=True)
	#df_mean = DATA[DATA.index % 4 == 2].copy(deep=True)
	#df_std = DATA[DATA.index % 4 == 3].copy(deep=True)
	#Old ^, made new to not confuse the script

	#dfs = [df_min, df_max, df_mean, df_std]

	#def transpose(index, dataframe):
	def transpose(dataframe):
		df = dataframe.T
		df.columns = ['et-1/0/1-star', 'et-0/0/0-star', 'et-1/0/0-star', 'et-0/1/0-star', 'et-0/1/0-600w','et-1/0/2-600w']
		df.drop(['Unnamed: 0', 'Unnamed: 1'], axis = 0, inplace=True)
		df = dataframe.drop(['Unnamed: 0', 'Unnamed: 1'], axis = 1)
		df['nodes'] = ['et-1/0/1-star', 'et-0/0/0-star', 'et-1/0/0-star', 'et-0/1/0-star', 'et-0/1/0-600w','et-1/0/2-600w']
		#Old ^ 
		df = pd.Series(df['0'].values,index=df.nodes).to_dict()
		return df
	
	#for index, df in enumerate(dfs):
	#	transpose(index,df)

	dfchimin = transpose(df_chimin)	
	dfchimax = transpose(df_chimax)
	dfchimean = transpose(df_chimean)
	dfchistd = transpose(df_chistd)
	return dfchimin, dfchimax, dfchimean, dfchistd
	
"""def RBIN(metadata):
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
	#print(df)
	return df"""

def AGLT2RTR(metadata):
	metadata = str(metadata)
	aglt2rtrpath = os.environ["aglt2rtr"]
	#outpath = "../Output/Raw/AGLT2/aglt2rtr"
	rtrpppath = os.environ["rtrpp"]
	#outpath = "../Output/Raw/aglt2rtr/pp
	
	#Router path
	if os.path.isdir(aglt2rtrpath):
		print("Path exists: ", aglt2rtrpath)
	else:
		print("Path does not exist")

	#Router/pp path
	if os.path.isdir(rtrpppath):
		print("Path exists: ", rtrpppath)
	else:
		print("Path does not exist")	
	
	csvfiles = glob.glob(os.path.join(rtrpppath, 'AGLT2RTR_{}_*.csv'.format(metadata)))
	csvfiles = sorted(csvfiles)
	print(csvfiles)
	dataframes = []
	for files in csvfiles:
		df = pd.read_csv(files)
		dataframes.append(df)
	result = pd.concat(dataframes, ignore_index=True)
	DATA = pd.DataFrame(data = result)
	DATA = DATA.round(4)	

	df_min = DATA[DATA.index % 4 == 0].copy(deep=True)
	df_max = DATA[DATA.index % 4 == 1].copy(deep=True)
	df_mean = DATA[DATA.index % 4 == 2].copy(deep=True)
	df_std = DATA[DATA.index % 4 == 3].copy(deep=True)

	def transpose(dataframe):
		df = dataframe.T
		df.columns = ['rtr-1-eth-1-51', 'rtr-1-eth-1-52', 'rtr-2-eth-1-51', 'rtr-2-eth-1-52']
		df.drop(['Unnamed: 0'], axis = 0, inplace=True)
		df = dataframe.drop(['Unnamed: 0'], axis = 1)
		df['Routers'] = ['rtr-1-eth-1-51', 'rtr-1-eth-1-52', 'rtr-2-eth-1-51', 'rtr-2-eth-1-52']
		df = pd.Series(df['srv'].values,index=df.Routers).to_dict()
		return df
	dfmin = transpose(df_min)
	dfmax = transpose(df_max)
	dfmean = transpose(df_mean)
	dfstd = transpose(df_std)
	return dfmin, dfmax, dfmean, dfstd
