#!/bin/bash
# @author Adam Pelletier
# @version 1.0


# read arguments
while getopts "r:s:" option
do
    case "$option" in
    s) sampleFile=$OPTARG;;
    r) reference=$OPTARG;;
    esac
done

# set global variables for the script

line_index=$(($AWS_BATCH_JOB_ARRAY_INDEX + 1))

sampleID=$(awk -v line=$line_index -F '\t' 'NR==line{print $1;exit}' $sampleFile)
fastqDir=$(awk -v line=$line_index -F '\t' 'NR==line{print $3;exit}' $sampleFile)


cellranger-atac count \
            --id=$sampleID \
            --reference=$genome
            --fastqs=$fastqDir \
            --sample=$sampleID \
            --localcores = 32 \
            --expect-cells = 10000 \ 
            --localmem = 185 