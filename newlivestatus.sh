#!/bin/bash
#hosts=('umfs06' 'umfs20' 'umfs23' 'umfs26' 'umfs09' 'umfs16' 'umfs21' 'umfs24' 'umfs27' 'umfs11' 'umfs19' 'umfs22' 'umfs25' 'umfs28' 'umfs29' 'umfs30' 'umfs31' 'umfs32' 'umfs33' 'umfs:s34')
#array=('CPU load' 'CPU utilization' 'Disk IO SUMMARY' 'Memory')
#array2=('load5' 'util' 'disk_utilization' 'mem_available')
#for host in ${hosts[@]}; do 
#    for ((i=0; i<${#array[@]}; i++)); do 
#echo "${host} for service ${array[$i]} and data ${array2[$i]}"
#comdata="lq \"GET services\nFilter: host_name = ${host}\nFilter: service_description = ${array[$i]}\nColumns:  rrddata:m1:${array2[$i]}.max,1,*:${1}:${2}:1\nOutputFormat: json\"" 
com1="su - atlas"
ssh -T root@omd <<-EOF 2>&1 >> ${3}/livestatus_all.txt #.json
cd checkmk-nginx-le
    docker exec -i omd /bin/bash -c "${com1}" <<-EOF2 
        bash /omd/sites/atlas/aglt2script/testjem.sh ${1} ${2}
        #Need to change name of 'testjem.sh' 
EOF2
EOF
#done
#done