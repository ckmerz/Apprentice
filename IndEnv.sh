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
export MAINDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && cd ../Shinano && pwd )"
mkdir ${MAINDIR}/Output/Output_${currentdate}
export outdir=${MAINDIR}/Output/Output_${currentdate}

mkdir ${outdir}/Dict
export dict=${outdir}/Dict 

mkdir ${outdir}/Raw
export raw=${outdir}/Raw 
    mkdir ${raw}/AGLT2
    export aglt2=${raw}/AGLT2
    mkdir ${raw}/AGLT2/checkmk #stores AGLT2 node data coming from checkmk
    #rename to dcache or umfs_servers 
    export checkmk=${aglt2}/checkmk
    mkdir ${raw}/AGLT2/checkmk/livestatus #raw json in livestatus_all.txt. livestatus_pp.txt same but brackets stripped by removechar.sh
    export checkmkls=${aglt2}/checkmk/livestatus 
    mkdir ${raw}/AGLT2/checkmk/pp #same as livestatus but data is organized/labeled
    export checkmkpp=${aglt2}/checkmk/pp
    
    mkdir ${raw}/AGLT2/aglt2rtr #same format as /checkmk but gets router data instead
    export aglt2rtr=${aglt2}/aglt2rtr
    mkdir ${raw}/AGLT2/aglt2rtr/livestatus
    export rtrls=${aglt2rtr}/livestatus
    mkdir ${raw}/AGLT2/aglt2rtr/pp
    export rtrpp=${aglt2rtr}/pp

    mkdir ${raw}/AGLT2_CHI
    export aglt2chi=${raw}/AGLT2_CHI
    mkdir ${raw}/RBIN
    export rbin=${raw}/RBIN

mkdir ${outdir}/Time
export time=${outdir}/Time

#source ${MAINDIR}/env/bin/activate
python ${MAINDIR}/AGLT2_ind_nv.py > ${aglt2}/checkmk.log 2>&1 
python ${MAINDIR}/AGLT2CHI_ind.py > ${aglt2chi}/aglt2chi.log 2>&1
python ${MAINDIR}/RBIN_ind.py > ${rbin}/rbin.log 2>&1
#Add an except section for this because sometimes we get data, sometimes not. If it doesn't work
#it breaks the dict_maker! 
python ${MAINDIR}/Router_ind.py > ${aglt2}/aglt2rtr.log 2>&1
python ${MAINDIR}/dict_maker.py > ${dict}/dict_output.txt 2>&1

#rm **/*.pyc: Needed for final version? 