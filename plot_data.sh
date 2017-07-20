#! /bin/bash
if [ $# -ne 1 ] && [ $# -ne 5 ] ; then 
  echo "ERROR: need one argument at least: the file to analyse. If you want to add a time window, then need 3 arguments in a dat command friendly dormat, before the directory argument"
  exit 1
fi
##################################################################
if [ $# -eq 1 ] ; then
  if [ -d $1 ] ; then
    echo "ERROR: $1 is a directory"
    exit 1
  fi
  if ! [ -e $1 ] ; then
    echo "ERROR: $1 does not exist or is not a file"
    exit 1
  fi
  echo "Plotting for full data time"
  if ! [ -d $(dirname $1)/full_time ] ; then
    mkdir $(dirname $1)/full_time
  fi
  sed -i 's/[[:blank:]]/ /g' $1
  python pyfiles/plot_data.py 0 1 $1 $(dirname $1)/full_time
  exit 0
fi
##################################################################
if [ -d $5 ] ; then
  echo "ERROR: $5 is a directory"
  exit 1
fi
if ! [ -e $5 ] ; then
  echo "ERROR: $5 does not exist or is not a file"
  exit 1
fi
if ! date -d "$1 $2" > /dev/null 2>&1 ; then
 echo "ERROR: invalide start time format"
 exit 1
fi
if ! date -d "$3 $4" > /dev/null 2>&1 ; then
 echo "ERROR: invalide start time format"
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
sed -i 's/[[:blank:]]/ /g' $5
numlines=$(wc -l < $5)
absolute_start=$(sed '2q;d' $5 | cut -d ' ' -f 1 )
absolute_end=$(sed "${numlines}q;d" $5 | cut -d ' ' -f 1 )
if [ $start -lt $absolute_start ] ; then
 echo "Start time lower than data's initial time: will take data's initial time instead"
 start=$absolute_start
 total_initial=true
fi
if [ $end -gt $absolute_end ] ; then
 echo "End time greater than data's final time: will take data's final time instead"
 end=$absolute_end
 total_final=true
fi
if [ $start -gt $absolute_end ] ; then
 echo "ERROR: Start time greater than data's final time"
 exit 1
fi
if [ $end -lt $absolute_start ] ; then
 echo "ERROR: End time lower than data's start time"
 exit 1
fi
##################################################################
if [ $total_initial ] && [ $total_final ] ; then
  echo "Plotting for full data time"
  if ! [ -d $(dirname $5)/full_time ] ; then
    mkdir $(dirname $5)/full_time
  fi
  python pyfiles/plot_data.py 0 1 $5 $(dirname $5)/full_time
  exit 0
fi
##################################################################
direc="$start_string---$end_string"
if ! [ -d $(dirname $5)/$direc ] ; then
  mkdir $(dirname $5)/$direc
fi

python pyfiles/plot_data.py $start $end $5 $(dirname $5)/$direc
  
