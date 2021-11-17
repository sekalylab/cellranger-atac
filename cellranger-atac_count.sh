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

## parentDir=$(dirname $(dirname "$fastqDir"))
## parentDir="${parentDir}/runs"
parentDir=$(awk -v line=$line_index -F '\t' 'NR==line{print $4;exit}' $sampleFile)


currentDate=$(date +"%Y-%m-%d %X")
echo -ne "$currentDate: Running cellranger-atac..."

cd $parentDir

echo "Switching to $parentDir directory..."

cmd="cellranger-atac count \
		       --id=$sampleID \
                       --reference=$reference \
                       --fastqs=$fastqDir \
                       --sample=$sampleID \
                       --localcores=32   \
                       --localmem=185"

echo $cmd

eval $cmd
echo "done"
