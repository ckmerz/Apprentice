com1="su - atlas"
ssh -T root@omd <<-EOF 2>&1 >> ${3}/livestatus_all.txt #.json
cd checkmk-nginx-le
    docker exec -i omd /bin/bash -c "${com1}" <<-EOF2 
        bash /omd/sites/atlas/aglt2script/aglt2rtr.sh ${1} ${2}
        #bash /omd/sites/atlas/aglt2script/testjem.sh ${1} ${2}
        #Old ^, made a new bash for the router part
EOF2
EOF
