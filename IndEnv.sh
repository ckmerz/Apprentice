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

mkdir ${outdir}/Dict
export dict=${outdir}/Dict 

mkdir ${outdir}/Raw
export raw=${outdir}/Raw 
    mkdir ${raw}/AGLT2
    export aglt2=${raw}/AGLT2
    mkdir ${raw}/AGLT2/checkmk
    export checkmk=${aglt2}/checkmk
    mkdir ${raw}/AGLT2/checkmk/livestatus
    export checkmkls=${aglt2}/checkmk/livestatus
    mkdir ${raw}/AGLT2/checkmk/pp
    export checkmkpp=${aglt2}/checkmk/pp
<<con 
Stores four data types from various AGLT2 nodes coming from checkmk. 
/AGLT2/livestatus houses the raw json data in _all.txt. Brackets are stripped by removechar.sh 
section and new file is made with the data minus the brackets in _pp.txt. Not human friendly 
though. /pp has the same data, but it's organized and labeled so it's human readable.
Used to seperate the regular data from the router data
con

<<con
    mkdir ${raw}/AGLT2/livestatus
    export checkmkls=${aglt2}/livestatus
    mkdir ${raw}/AGLT2/pp
    export pp=${aglt2}/pp
    Old ^, added checkmk & aglt2rtr as higher up directories (dirs) to seperate the
    checkmk data from the router data
con
    mkdir ${raw}/AGLT2/aglt2rtr
    export aglt2rtr=${aglt2}/aglt2rtr
    mkdir ${raw}/AGLT2/aglt2rtr/livestatus
    export rtrls=${aglt2}/livestatus
    mkdir ${raw}/AGLT2/aglt2rtr/pp
    export rtrpp=${aglt2}/pp
    #Makes the router dir and it's sub-dirs 
    #Want data for both routers (all 4 connections)
    #in the same dir but labled so we know which of the 4 you're looking at
    #Would want it to look like /pp dir
    #Ex: AGLT2-rtr1-1/51_in.csv or AGLT2-rtr2-1/52_out.csv
<<con
    mkdir ${raw}/AGLT2/interface_ethernet
    export ie=${aglt2}/interface_ethernet
    mkdir ${raw}/AGLT2/interface_ethernet/livestatus
    export iels=${aglt2}/livestatus
    mkdir ${raw}/AGLT2/interface_ethernet/pp
    export iepp=${aglt2}/pp
Think this is wrong so don't think I'll use, kept in case this is actually right lol  
con
    
    
    
    mkdir ${raw}/AGLT2_CHI
    export aglt2chi=${raw}/AGLT2_CHI
    mkdir ${raw}/RBIN
    export rbin=${raw}/RBIN

mkdir ${outdir}/Time
export time=${outdir}/Time
#Do tabs mean anything in bash? Did this to make it easier to read. Especially if 
#anything's added under /Dict or /Time 

<<con
source ${MAINDIR}/env/bin/activate
python ${MAINDIR}/AGLT2_ind_nv.py > ${aglt2}/aglt2.log 2>&1 
python ${MAINDIR}/AGLT2CHI_ind.py > ${aglt2chi}/aglt2chi.log 2>&1
python ${MAINDIR}/RBIN_ind.py > ${rbin}/rbin.log 2>&1
wait
python ${MAINDIR}/Scripts/AGLT2CHI_ind.py > ${aglt2chi}/aglt2chi.log 2>&1
python ${MAINDIR}/Scripts/RBIN_ind.py > ${rbin}/rbin.log 2>&1
wait
python ${MAINDIR}/Scripts/dict_maker.py > ${dict}/dict_output.txt 2>&1
wait
rm **/*.pyc

python ${MAINDIR}/dict_maker.py > ${dict}/dict_output.txt 2>&1
wait
con
#Old ^, ran the scripts when they were seperate so don't need anymore?
#Assuming this section just becomes:

source ${MAINDIR}/env/bin/activate
python ${MAINDIR}/Scripts/Apprentice.py > ${apprentice}/apprentice.log 2>&1
#What's this part: > ${apprentice}/apprentice.log 2>&1 
#Should it be > ${aglt2}/aglt2.log 2>&1 

#Will the /dict_output.txt part be a problem here? 
#Rename Apprentice to Shinano? 
#rm **/*.pyc: Needed for final version? 

######==newlivestatus.sh==######
com1="su - atlas"
ssh -T root@omd <<-EOF 2>&1 >> ${3}/livestatus_all.txt #.json
cd checkmk-nginx-le
    docker exec -i omd /bin/bash -c "${com1}" <<-EOF2 
        bash /omd/sites/atlas/aglt2script/aglt2rtr.sh ${1} ${2}
        #bash /omd/sites/atlas/aglt2script/testjem.sh ${1} ${2}
        #Old ^, made a new bash for the router part
EOF2
EOF

######==removechar.sh==######
cat ${1}/livestatus_all.txt |  awk '{ print substr( $0, 4 ) }' | awk '{ print substr( $0, 1, length($0)-3) }' > ${1}/livestatus_pp.txt
#Takes livestatus_all.txt inside of /Raw, makes a new file w/ the same data minus 
#the brackets and names the new file livestatus_pp.txt (also under /Raw). 