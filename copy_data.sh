#! /bin/bash

for Dir in ./dir_* ; do
  dir_data=$(basename $Dir)
  if ! [ -d "$dir_data" ] ; then
    continue
  fi
  if ! ls $dir_data/Data_* 1> /dev/null 2>&1; then
    continue
  fi
  cp $dir_data/Data_* ./
done

rsync -avh -e ssh wa105db@lxplus.cern.ch:~/tools/pcotte_getdata/Data_* ./

if ! ls Data_* 1> /dev/null 2>&1; then
  echo "No Data file transfered"
  exit 1
fi

for data in ./Data_* ; do
  File=$(basename $data)
  if [ -d "$File" ] ; then
    echo "$File is a directory. Skipping it."
    continue
  fi
  direc=$(echo $File | sed -r 's/Data_//g')
  direc="dir_$direc"
  if [ -d "$direc" ] ; then
    rm $File
    continue
 fi
  mkdir $direc
  file=$(basename $File)
  mv $file $direc/
done
