# cellranger-atac
## Sequencing pipeline
Contains scripts for 10X single-cell ATAC-seq preprocessing

<!-- badges: start -->
![GitHub last commit](https://img.shields.io/github/last-commit/sekalylab/cellranger-atac/main)
<!-- badges: end -->

## Dependencies
- Python (version 3.9.0)
    - boto3
    - pandas
- AWS CLI v2

## Installation
A Miniconda environment containing all prerequisites is already installed on the front-end. Instructions on how to access it is located [here](https://github.com/sekalylab/cellranger-atac/blob/main/conda-env-setup.md)
This only needs to be done once per user.

## Function

The CellRanger-ATAC pipeline aligns reads from fastq files to a reference genome. 

Files can be supplied on the mounted EFS of the Sekaly lab, or by providing a S3 URI (e.g. s3://patru-emory-genomics-uploads/test-data/) where the files are stored. 


Files will first be **1.transferred** to the EFS automatically to a temporary directory, **including the specified reference**, followed by **2.alignment/counting**.

Unless cancelled by the *--aggregate* flag, an **3. aggregate** step will be performed to combine all samples into a single dataset, including a Loupe Browser file. 

Finally, a **4. Clean up** step will be performed to organize the data into a more useful structure, upload it to a targetted S3 bucket and remove temporary files from the EFS.    


## Usage
#### Running the cellranger-atac pipeline
The pipeline is already located on the EFS (/mnt/efs/pipelines/cellranger-atac/) and does NOT need to be cloned from Github on each use.
Simply connect to the front-end [instructions here](https://github.com/sekalylab/cellranger-atac/blob/main/running-on-aws.md) and launch the pipeline using the master script. 


```bash
python cellranger-atac_master.py --help  

Required arguments:  
-i;--input = [i]nput location of files to transfer: can be a S3 bucket or a local absolute path on the EFS (required))  
-o; --output = [o]utput S3 bucket for file cleanup (required)  
-e;--email = [e]mail for notifications of pipeline status

Optional arguments:
-r; --reference = [r]eference for alignment. Defaults to 'GRCh38'. Choices are 'GRCh38' and 'mm10'
-n;--name = [n]ame for run. Will be used to produce files with a distinctive name. Otherwise a generic name will be made
--aggregate = Deactivate the aggregation portion of the pipeline. Aggregation is performed by default.
--normalize = Normalization mode for aggregation step. Choices are 'depth' and 'none'; default is 'depth'. 
--keep = Does not delete the files on the EFS after run completion. 

```


Example call :

```bash 

python /mnt/efs/pipelines/cellranger-atac/cellranger-atac_master.py \
	 -i s3://patru-emory-genomics-uploads/test-data/ \
	 -o s3://patru-users/userName/test-data \
	 -e slim.fourati@emory.edu \
	 -r GRCh38 \
	 -n Ashish_p123456

```
