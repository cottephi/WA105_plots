#! /bin/bash

scp wa105db@lxplus.cern.ch:~/tools/pcotte_getdata/Data_* ./
for data in "./Data_*" ; do
  if [ -d $data ] ; then
    echo "ERROR: $data is a directory"
    exit 1
  fi
  direc=$(echo $data | sed -r 's/Data_//g')
  if [ -d $direc ] ; then
    echo "Folder $direc already exists. Skipping it."
    continue
 fi
  mkdir $direc
  file=$(basename $data)
  mv $file $direc/
done
