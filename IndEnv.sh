#!/bin/bash

#****************************************#
#		IndEnv.sh
#		Author: Jem Guhit
#		April 24, 2021

#	Runs Independent Environment 
#	scripts and saves them to raw
#	and dict outputs
#****************************************#
export PYTHONPATH=/lustre/umt3/user/guhitj/Gitlab/netbasilisk/XRootD/AGLT2/Scripts/IndEnv/env/bin/python
export PATH=/lustre/umt3/user/guhitj/Gitlab/netbasilisk/XRootD/AGLT2/Scripts/IndEnv/env/bin/:/usr/bin:/bin:
export currentdate=`date +"%Y%m%d_%H%M"`
export date_5=`date +"%Y%m%d_%H%M" --date='5 minutes ago'`
export currentdateunix=`date +%s`
export dateunix_5=`date +%s --date='5 minutes ago'`
export MAINDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && cd ../newAGLT2 && pwd )"
mkdir ${MAINDIR}/Output/Output_${currentdate}
export outdir=${MAINDIR}/Output/Output_${currentdate}
mkdir ${outdir}/Raw
export raw=${outdir}/Raw 
mkdir ${raw}/AGLT2
export aglt2=${raw}/AGLT2
mkdir ${raw}/AGLT2/livestatus
export checkmkls=${aglt2}/livestatus
mkdir ${raw}/AGLT2/pp
export pp=${aglt2}/pp
mkdir ${outdir}/Time
export time=${outdir}/Time
#mkdir${raw}/AGLT2/aglt2rtr
#export rtr=${aglt2}/aglt2rtr 
#Correct? Also, want data for both routers (all 4 connections)
#in the same dir but labled so we know which of the 4 you're looking at

#Setting up dirs for the router connections

#mkdir ${raw}/AGLT2_CHI
#export aglt2chi=${raw}/AGLT2_CHI
#mkdir ${raw}/RBIN
#export rbin=${raw}/RBIN
#Temp stopped these ^ 

mkdir ${outdir}/Dict
export dict=${outdir}/Dict 
#source ${MAINDIR}/env/bin/activate
python ${MAINDIR}/AGLT2_ind_nv.py > ${aglt2}/aglt2.log 2>&1 
#python ${MAINDIR}/AGLT2CHI_ind.py > ${aglt2chi}/aglt2chi.log 2>&1
#python ${MAINDIR}/RBIN_ind.py > ${rbin}/rbin.log 2>&1
#Temp stopped these ^ 
wait

<<con
python ${MAINDIR}/Scripts/AGLT2CHI_ind.py > ${aglt2chi}/aglt2chi.log 2>&1
python ${MAINDIR}/Scripts/RBIN_ind.py > ${rbin}/rbin.log 2>&1
wait
python ${MAINDIR}/Scripts/dict_maker.py > ${dict}/dict_output.txt 2>&1
wait

rm **/*.pyc
con
python ${MAINDIR}/dict_maker.py > ${dict}/dict_output.txt 2>&1
#wait

#Assuming this ^ section will only be: python ${MAINDIR}/where_ever Apprentice.py > ${?}

#rm **/*.pyc
