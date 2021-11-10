#!/bin/bash
# @author Adam Pelletier
# @version 0.1

# read arguments
while getopts "d:o:" option
do
    case "$option" in
    d) inputData=$OPTARG;;
    o) outputDir=$OPTARG;;
    esac
done

line_index=$(($AWS_BATCH_JOB_ARRAY_INDEX + 1))

fastq=$(awk -v line=$line_index -F '\t' 'NR==line{print $1;exit}' $inputData)

currentDate=$(date +"%Y-%m-%d %X")
echo -ne "$currentDate:  Running FASTQC..."
fastqc $fastq -o $outputDir -f fastq
echo "done"
