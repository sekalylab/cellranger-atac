#!/bin/bash
# @author Adam Pelletier
# @version 1.0


# read arguments
while getopts "r:p:i:c::n:a:" option
do
    case "$option" in
    p) pathDir=$OPTARG;;
    r) reference=$OPTARG;;
    i) id=$OPTARG;;
    c) csv=$OPTARG;;
    n) normalize=$OPTARG;;
    a) analyze=$OPTARG;;
    esac
done

# set global variables for the script


currentDate=$(date +"%Y-%m-%d %X")
echo -ne "$currentDate: Running cellranger-atac aggr..."

cd $pathDir

cmd="cellranger-atac aggr --id=$id --reference=$reference --csv=$csv --normalize $normalize --nosecondary"
echo $cmd
eval $cmd


echo -ne "$currentDate: Running cellranger-atac reanalyze..."
cmd="cellranger-atac reanalyze --id=${id}_reanalyze --reference=$reference --agg=$csv --peaks ${id}/outs/peaks.bed --fragments ${id}/outs/fragments.tsv.gz --params $analyze"

echo $cmd
eval $cmd


echo "done"

