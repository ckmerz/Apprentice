cat ${1}/livestatus_all.txt |  awk '{ print substr( $0, 4 ) }' | awk '{ print substr( $0, 1, length($0)-3) }' > ${1}/livestatus_pp.txt

#cat ${3}/livestatus_all.txt |  awk '{ print substr( $0, 4 ) }' | awk '{ print substr( $0, 1, length($0)-3) }'
#2>&1 >> ${3}/livestatus_all.txt