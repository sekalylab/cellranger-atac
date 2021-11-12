#!/bin/bash
# @author Adam Pelletier
# @version 1.0

# read arguments
while getopts "r:s:" option
do
    case "$option" in
    s) s3File=$OPTARG;;
    esac
done

# set global variables for the script

line_index=$(($AWS_BATCH_JOB_ARRAY_INDEX + 1))

while read line;do
    source=$(echo $line | cut -d " " -f 1)
    dest=$(echo $line | cut -d " " -f 3)
    cmd="aws s3 cp $source $dest" 
    eval $cmd
done < <(awk -v line=$line_index -F "\t" '{ if ( $2 == line ) { print } }' $s3File)
