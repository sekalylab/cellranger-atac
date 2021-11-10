###                                            -*- Mode: Python -*-
###                                            -*- coding UTF-8 -*-
### s3_transfer_functions.py
### Copyright 2021 RPM Bioinfo Solutions
### Author :  Adam-Nicolas Pelletier
### Last modified On: 2021-11-05
### Version 1.00


import re
import boto3
import botocore
from pathlib import Path
from datetime import datetime
from botocore.client import ClientError
import pandas as pd
import numpy as np
import os


def extract_bucket(uri):
	s3_sub = re.sub(r's3://', '', uri)
	bucket = re.sub(r'/.*', '', s3_sub)
	return bucket

def extract_subdir(uri):
	s3_sub = re.sub(r's3://', '', uri)
	subdirsplit = s3_sub.split("/")
	subdir = "/".join(subdirsplit[2:])
	return subdir

def s3_check(uri, resource):
	reg = re.compile(r's3://')  
	s3_contain = re.search(reg, uri)
	if s3_contain == None:
		return False
	else:
		bucket = extract_bucket(uri)
		
		try:
			resource.meta.client.head_bucket(Bucket=bucket)
			return True
		except ClientError:
			print("The bucket %s does not exist or you have no access." % bucket)  # The bucket does not exist or you have no access.
			sys.exit()

def s3_file_list(uri, resource):
	bucket = extract_bucket(uri)
	my_bucket = resource.Bucket(bucket)
	fileLS = [] 
	for my_bucket_object in my_bucket.objects.all() :
		s3_path = "s3://" + bucket + "/" + my_bucket_object.key
		fileLS.append(s3_path)

	reg = re.compile(uri)
	fileLS_filt = [i for i in fileLS if re.search(reg, i)]
	return fileLS_filt

def nested_batches_list(file_list_uri, n_batches):
	ind = 0
	split = np.array_split(file_list_uri, n_batches)

	nested = []
	for array in range(0, len(split)):
		df = pd.DataFrame(list(split[array]),
	 		columns =['Source'])
		df["Batch"] = array + 1

		nested.append(df)

	return(pd.concat(nested, ignore_index= True))
	


def subdirectory_check(file_list, prefix):
	sample_dict = {}
	for i in file_list:
		sample = os.path.dirname(re.sub(prefix, "", i))
		if sample == "":
			print("Data is not divided in subdirectories. Organize data per sample and relaunch. Aborting...")
			sys.exit()
		elif sample in sample_dict:
			sample_dict[sample].append(i)
		else:
			sample_dict[sample] = [i]
	return(sample_dict)


def sample_batch(file_list, add_batches, prefix):
	sample_dict = subdirectory_check(file_list, prefix)
	df = pd.DataFrame.from_dict(sample_dict).melt(var_name = "Sample", value_name = "Source")
	
	df["Batch"] = pd.factorize(df["Sample"])[0]
	df["Batch"] = df["Batch"] + 1 + add_batches
	df["Batch"] = df["Batch"]
	return(df)



