#!/bin/bash
# @author Adam Pelletier
# @version 0.1


keep=false
aggregate=true
# read arguments
while getopts "p:k:o:n:a:" option
do
    case "$option" in
    p) pathdir=$OPTARG;;
    k) keep=true;;
    o) output_bucket=$OPTARG;;
    n) name=$OPTARG;;
    a) aggregate=false;;
    esac
done

if [ "$pathdir" == "/mnt" ]; then
    echo "Trying to use cleaning script on root of mounted EFS is not permitted. Aborting..."
    exit
fi

cd $pathdir

mkdir bam
mkdir filtered_matrix
mkdir raw_matrix
mkdir bed
mkdir summary
mkdir fragments
mkdir loupe
mkdir singlecell

for i in runs/*/; 
do
    sample=$(basename $i)
    mkdir -p bam/$sample
    mv runs/${sample}/outs/*.bam bam/${sample}/
    mv runs/${sample}/outs/*.bai bam/${sample}/


    mkdir -p filtered_matrix/$sample
    mv runs/${sample}/outs/filtered*.h5 filtered_matrix/${sample}/

    mkdir -p raw_matrix/$sample
    mv runs/${sample}/outs/raw*.h5 raw_matrix/${sample}/

    mkdir -p bed/$sample
    mv runs/${sample}/outs/*.bed bed/${sample}/
    

    mkdir -p fragments/$sample
    mv runs/${sample}/outs/fragments* fragments/${sample}/


    mkdir -p loupe/$sample
    mv runs/${sample}/outs/cloupe.cloupe loupe/${sample}/cloupe.cloupe


    mkdir -p singlecell/$sample
    mv runs/${sample}/outs/singlecell.csv singlecell/${sample}/singlecell.csv
    

    mkdir -p summary/$sample
    mv runs/${sample}/outs/analysis/ summary/${sample}/analysis/
    mv runs/${sample}/outs/summary.csv summary/${sample}/summary.csv
    mv runs/${sample}/outs/summary.json summary/${sample}/summary.json
    mv runs/${sample}/outs/peak_annotation.tsv summary/${sample}/peak_annotation.tsv
    mv runs/${sample}/outs/web_summary.html summary/${sample}/web_summary.html

done


aws s3 sync bam $output_bucket/bam
aws s3 sync filtered_matrix $output_bucket/filtered_matrix
aws s3 sync raw_matrix $output_bucket/raw_matrix
aws s3 sync bed $output_bucket/bed
aws s3 sync summary $output_bucket/summary
aws s3 sync fragments $output_bucket/fragments
aws s3 sync loupe $output_bucket/loupe
aws s3 sync single $output_bucket/singlecell

if aggregate == true; then
    aws s3 sync $name/outs $output_bucket/aggregate
    aws s3 sync $name_reanalyze/outs $output_bucket/reanalyze
fi

if keep == false; then
    cd ..
    rm -R pathdir
fi


