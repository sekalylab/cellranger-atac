#!/bin/bash
# @author Adam Pelletier
# @version 1.0


# read arguments
while getopts "r:p:i:c::n" option
do
    case "$option" in
    p) pathDir=$OPTARG;;
    r) reference=$OPTARG;;
    i) id=$OPTARG;;
    c) csv=$OPTARG;;
    n) normalize=$OPTARG;;
    esac
done

# set global variables for the script


currentDate=$(date +"%Y-%m-%d %X")
echo -ne "$currentDate: Running cellranger-atac..."

cd $pathDir

cmd="cellranger-atac aggr  --id=$id --reference=$reference --csv=$csv --normalize $normalize"


eval $cmd

echo "done"

