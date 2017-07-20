#! /bin/bash
if [ $# -ne 5 ] ; then 
 echo "ERROR: need 5 arguments: start and end moments, both must have date and time (like 2017/06/28 17:00:00 2017/06/29 17:00:00), plus the parameters to record, written in a file"
 exit 1
fi
if ! date -d "$1 $2" > /dev/null 2>&1 ; then
 echo "ERROR: invalide start time format"
 exit 1
fi
if ! date -d "$3 $4" > /dev/null 2>&1 ; then
 echo "ERROR: invalide end time format"
 exit 1
fi
start_string=$(echo "$1 $2" | tr / - )
end_string=$(echo "$3 $4" | tr / - )
start=$(date -d "$start_string" "+%s")
end=$(date -d "$end_string" "+%s")
start_string=$(echo "$start_string" | tr " " _ )
end_string=$(echo "$end_string" | tr " " _ )
if [ $start -ge $end ] ; then
 echo "ERROR: start time greater than end time"
 exit 1
fi
if [ $start -eq $end ] ; then
 echo "ERROR: start time equal to end time"
 exit 1
fi
now=$(date +%s)
if [ $end -gt $now ] ; then
 echo "ERROR: Time travel not developped yet"
 exit 1
fi

params=$5

./getData -s $start -e $end $(<$params) > "Data_$start_string""_to_""$end_string.txt"

exit 0
