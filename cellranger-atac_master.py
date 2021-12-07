###                                            -*- Mode: Python -*-
###                                            -*- coding UTF-8 -*-
### cellranger-atac_master.py
### Author :  Adam-Nicolas Pelletier
### Last modified On: 2021-08-10
### Version 1.01


import os
import pandas as pd
import numpy as np
import subprocess
import sys
import argparse
import re
import boto3
import botocore
from pathlib import Path
from datetime import datetime
from glob import glob
import builtins
import shutil
from aws_utils_patru.aws_notifications import *
from aws_utils_patru.s3_transfer import *

########################################################################################################################################################
########################################################## USER INPUT  AND OUTPUT ######################################################################


cwd = os.path.dirname(os.path.realpath(__file__))

pd.options.mode.chained_assignment = None  # default='warn

prof = boto3.session.Session(profile_name = "tki-aws-account-310-rhedcloud/RHEDcloudAdministratorRole")
client = boto3.client('batch', region_name="us-east-2")
s3 = boto3.resource('s3', region_name="us-east-2")
s3_client = boto3.client('s3', region_name="us-east-2")
events = boto3.client('events', region_name="us-east-2")
sns = boto3.client('sns', region_name="us-east-2")


parser = argparse.ArgumentParser(description="""launches the CellRanger-ATAC preprocessing pipeline""" )
parser._action_groups.pop()
required = parser.add_argument_group('required arguments')
optional = parser.add_argument_group('optional arguments')


required.add_argument("-i","--input", required=True,
					help="[i]nput location of files to transfer: can be a S3 bucket or a local absolute path on an EC2 instance (required)")
required.add_argument("-o","--output", required=True,
					help="[o]utput S3 bucket for file cleanup")
required.add_argument("-e","--email", required=True,
					help="[e]mail for notifications of pipeline status (required)")
optional.add_argument("-r", "--reference", default="GRCh38", choices=['GRCh38', 'mm10'],
					help="[r]eference for alignment. Defaults to 'GRCh38'")
optional.add_argument("-n", "--name", default="cellranger-ATAC-run",
					help="[n]ame for run")
optional.add_argument("--keep", action="store_true",
					help="keep files on the EFS after run. Defaults to FALSE")
optional.add_argument("--no_aggregate", action="store_true",
					help="Deactivate the aggregation portion of the pipeline. Aggregation is performed by default.")

optional.add_argument("--normalize", default="depth", choices=['depth', 'none'],
					help="Normalization mode for aggregation step.")

optional.add_argument("--test", action="store_true",
					help="Activates test mode, which does not launch on AWS Batch. Defaults to FALSE")
optional.add_argument("--reanalyze_params", default="docs/reanalyze_parameters.csv",
                                        help="Provide a customized parameter csv file for the reanalyze portion of the pipeline.")




args = parser.parse_args()



inputDir = args.input
outputDir = args.output
email = args.email
reference = args.reference
keep = args.keep
no_aggregate = args.no_aggregate
test = args.test
normalize = args.normalize
name = args.name
reanalyze = args.reanalyze_params
########################################################################################################################################################
########################################################################################################################################################
pd.options.display.max_colwidth = 150
date_time = datetime.now().strftime("%Y%m%d_%H%M%S")


# Scan for s3 validity
input_s3 = s3_check(inputDir, s3)
output_s3 = s3_check(outputDir, s3)

# Verify if output is a S3 location
if output_s3:
	pass
else:
	print("Invalid output location. Specify a valid S3 location. Aborting...")
	sys.exit()

#EFS check
efs_check = os.path.isfile("/mnt/efs/pipelines/efs_check.txt")
if(efs_check == False):
	print("Mounted EFS not found. Make sure you are connected to the front end node to launch pipeline. Exiting...")
	sys.exit()

def exit_strategy(dir):
	shutil.rmtree(dir)
	sys.exit()

#Check script directory
scriptLS = ["file_transfer.sh","cellranger-atac_count.sh", "cellranger-atac_aggr.sh", "cellranger-atac_clean.sh"]
script_check = all(item in os.listdir() for item in scriptLS)
if script_check is False:
        print("Not all expected scripts found in the current directory. Make sure to launch the pipeline from `/mnt/efs/pipelines/cellranger-atac` or a from the directory of a complete copy. ")
        sys.exit()

#Create temporary directory
tmpDir = "/mnt/" + "tmp_ATAC_" + date_time + "/"
tmpDir_write = re.sub("/mnt", "/mnt/efs", tmpDir)
os.mkdir(tmpDir_write.rstrip(os.sep))
tmpDir_abs = tmpDir_write.rstrip(os.sep)
os.mkdir(tmpDir_write + "runs")

#Copy scripts
tmp_script_write =  tmpDir_write + "scripts/"
shutil.copytree(os.getcwd(), tmp_script_write)
tmp_script = re.sub("efs/", "", tmp_script_write)

# Setup reference transfer 
reference_location = "s3://patru-genomes/" + reference + "/cellranger-arc"

reference_df = nested_batches_list(s3_file_list(reference_location, s3), 4)
reference_source = reference_df["Source"].tolist()
reference_df["Destination"] = [re.sub(reference_location,tmpDir + "reference", j) for j in reference_source]

## Name check
mntLS = [f for f in os.listdir("/mnt/efs") if os.path.isdir(os.path.join("/mnt/efs", f))]
if keep is True or test is True:
	if name in mntLS:
		print("A directory called %s is already located on the mounted EFS. Double-check if it's not a duplicate or name run differently. Aborting..." % name)
		exit_strategy(tmpDir_write) 

#Setup file transfer if files are on S3
if input_s3:
	fileLS_uri = s3_file_list(inputDir, s3)
	reg = re.compile('fastq.gz$')
	fileLS_uri = [i for i in fileLS_uri if re.search(reg, i)]
	if len(fileLS_uri) == 0:
		print("There are no fastqs in the specified URI. Try again. Exiting...")
		exit_strategy(tmpDir_write)

	sample_tf_df = sample_batch(fileLS_uri , reference_df["Batch"].max(), inputDir)  ## Dataframe for transer of individual files

	sample_tf_df["Destination"] = [re.sub(inputDir,tmpDir + "input/", j) for j in sample_tf_df["Source"].tolist()]
	
	df = pd.concat([reference_df,sample_tf_df.drop(columns = "Sample")], ignore_index = True)

	fileLS = df["Destination"].tolist()

	sample_df = sample_tf_df
	sample_df["Batch"] = pd.factorize(sample_df["Sample"])[0] + 1  #refactor to ignore reference transfer for downstream batch
	sample_df["path"] = [os.path.dirname(j) for j in sample_df["Destination"].tolist()] 
	sample_df = sample_df.drop(columns = ["Source", "Destination"]).drop_duplicates(ignore_index = True)


else :
	inputDir_abs = os.path.abspath(inputDir.rstrip(os.sep))
	fileLS = []
	for (dirpath, dirnames, filenames) in os.walk(inputDir_abs):
		fileLS += [os.path.join(dirpath, file) for file in filenames]
	reg = re.compile('fastq.gz$')
	fileLS =  [i for i in fileLS if re.search(reg, i)]
	if len(fileLS_uri) == 0:
		print("There are no fastqs in the specified directory. Try again. Exiting...")
		sys.exit()
	sample_df = sample_batch(fileLS, 0, inputDir)
	sample_df["path"] = [os.path.dirname(j) for j in sample_df["Source"].tolist()]
	sample_df["path"] = sample_df["path"].str.replace("efs/", "") 
	sample_df = sample_df.drop(columns= "Source").drop_duplicates(ignore_index = True)

	df = reference_df

shutil.copy2(os.path.abspath(reanalyze), tmpDir_write + "reanalyze_parameters.csv")

sample_df["outputDir"] = tmpDir + "runs/"


s3_transfer_file = tmpDir_write + "s3_transfer_batchlist.txt"
s3_transfer_batch = re.sub("efs/", "", s3_transfer_file)
df.to_csv(tmpDir_write + "s3_transfer_batchlist.txt", sep = "\t", index = False, header = False)

cellranger_file = tmpDir_write + "cellranger_atac_batch.txt"
cellranger_batch = re.sub("efs/", "", cellranger_file)

sample_df.to_csv(cellranger_file, sep = "\t", index = False, header = False)





#USER CHECK

print(sample_df)
print("\n\nDataset contains " + str(len(sample_df["Sample"].tolist())) + " samples:" )
#print(list(sample_dict.keys()))

prompt_check = False
while prompt_check is False:
	inp = input("\n\nContinue ? (y/n) :  ")
	print(inp)
	if inp.upper() == "Y":
		prompt_check = True
	elif inp.upper() == "N":
		exit_strategy(tmpDir_write)
	else:
		print("Invalid answer\n")


### Aggregate CSV
aggr_df = sample_df
aggr_df = sample_df.drop(columns= "Batch")
aggr_df['path'].replace({"input":"runs"}, regex = True, inplace=True)
aggr_df["path"] = aggr_df["path"] + "/outs"
aggr_df["fragments"] = aggr_df["path"] + "/fragments.tsv.gz"
aggr_df["cells"] = aggr_df["path"] + "/singlecell.csv"
aggr_df.rename(columns={'Sample':'library_id'}, inplace=True)
aggr_df = aggr_df.drop(columns = ["path", "outputDir"])
aggr_file = tmpDir_write + "aggr_csv.txt"
aggr_batch = re.sub("efs/", "", aggr_file)
aggr_df.to_csv(aggr_file, sep = ",", index = False)





NSAMPLE = df["Batch"].max()
jobName = "s3_transfer-job-%s" % date_time

if test is False:
	## File Transfer launch
	cmd = [	"bash",
			tmp_script + "file_transfer.sh",
			"-s", s3_transfer_batch]


	response = client.submit_job(
		jobName = jobName,
		jobQueue = "gsea-job-queue-3",
		jobDefinition = "s3-transfer-job-def-1",
		arrayProperties = {
			"size": NSAMPLE
		},
		containerOverrides = {
			"command": cmd,
			"memory": 16000
		},
		timeout = {
			"attemptDurationSeconds": 21600
		}
	)

	job_id = response['jobId']
	note = new_notification(job_id, jobName, date_time, events, sns, email)

	### CellRanger count
	NSAMPLE = sample_df["Batch"].max()
	jobName = "cellranger-atac-count-job-%s" % date_time

	cmd = ["bash", 
			tmp_script + "cellranger-atac_count.sh",
			"-s", cellranger_batch,
			"-r", tmpDir + "reference"]

	response = client.submit_job(
		jobName = jobName,
		jobQueue = "single-cell-job-queue-1",
		jobDefinition = "cellranger-atac-job-def-1",
		arrayProperties = {
			"size": NSAMPLE
		},
		dependsOn = [
					{
						"jobId" : job_id,
					}
		],
		containerOverrides = {
			"command": cmd,
			"memory": 192000,
			"vcpus" : 32
		},
		timeout = {
			"attemptDurationSeconds": 54000
		}
	
	)
	job_id = response['jobId']	
	note2 = add_notification(note, job_id, jobName, events, sns)

### CellRanger aggr
	if no_aggregate is False:
		jobName = "cellranger-atac-aggr-job-%s" % date_time

		cmd = ["bash", 
				tmp_script + "cellranger-atac_aggr.sh",
				"-c", aggr_batch,
				"-r", tmpDir + "reference",
				"-p", tmpDir,
				"-i", name.rstrip(os.sep),
				"-n", normalize,
				"-a", tmpDir + "reanalyze_parameters.csv"]

		response = client.submit_job(
			jobName = jobName,
			jobQueue = "single-cell-job-queue-1",
			jobDefinition = "cellranger-atac-job-def-1",
			dependsOn = [
						{
							"jobId" : job_id,
						}
			],
			containerOverrides = {
				"command": cmd,
				"memory": 192000,
				"vcpus" : 32
			},
			timeout = {
				"attemptDurationSeconds": 54000
			}
		
		)
		job_id = response['jobId']	
		note3 = add_notification(note2, job_id, jobName, events, sns)

### cleanup

	jobName = "cellranger-atac-clean-job-%s" % date_time

	cmd = ["bash", 
			tmp_script + "cellranger-atac_clean.sh",
			"-p", tmpDir,
			"-o", outputDir.rstrip("/"),
			"-n", name.rstrip(os.sep)]
	if keep is True:
		cmd.append("-k")
	if no_aggregate is True:
		cmd.append("-a")

	response = client.submit_job(
		jobName = jobName,
		jobQueue = "gsea-job-queue-3",
		jobDefinition = "s3-transfer-job-def-1",
		dependsOn = [
					{
						"jobId" : job_id,
					}
		],
		containerOverrides = {
			"command": cmd,
			"memory": 32000
		},
		timeout = {
			"attemptDurationSeconds": 21000
		}
	
	)
	job_id = response['jobId']
	if no_aggregate is True:
		note3 = add_notification(note2, job_id, jobName, events, sns)
	else:
		note4 = add_notification(note3, job_id, jobName, events, sns)


	print("Pipeline launched succesfully!")

elif test is True:
	os.rename(tmpDir_write, "/mnt/efs/"+ name)
