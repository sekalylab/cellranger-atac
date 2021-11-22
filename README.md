# cellranger-atac
## Sequencing pipeline
Contains scripts for 10X single-cell ATAC-seq preprocessing

<!-- badges: start -->
![GitHub last commit](https://img.shields.io/github/last-commit/sekalylab/cellranger-atac/main)
<!-- badges: end -->

## Dependencies
A Conda environment has been setup for all users to give access to dependencies and should be active by default upon login. 

- Python (version 3.9.5)
    - boto3
    - pandas
- AWS CLI v2



## Function

The CellRanger-ATAC pipeline aligns reads from fastq files to a reference genome. 

Files can be supplied on the mounted EFS of the Sekaly lab, or by providing a S3 URI (e.g. s3://patru-emory-genomics-uploads/test-data/) where the files are stored. 


Files will first be **1.transferred** to the EFS automatically to a temporary directory, **including the specified reference**, followed by **2.alignment/counting**.

Unless cancelled by the *--aggregate* flag, an **3. aggregate** step will be performed to combine all samples into a single dataset, including a Loupe Browser file. This also includes a secondary analysis (dimension reduction,clustering, differential peak enrichment) on either ALL cells if n < 100000, or a random subsample of 100k cells.  

Finally, a **4. Clean up** step will be performed to organize the data into a more useful structure, upload it to a targetted S3 bucket and remove temporary files from the EFS.    




## Usage
#### Directory structure
FASTQ files must be organized in nested subfolders for each sample. This is usually how single-cell files are provided by cores. The master script will perform a check for this structure and block execution if not set up the right way.

```bash
e.g. :   */mnt/efs/project_directory (or S3 URI)
				    /Sample1
					    /Sample1_R1.fastq.gz
					    /Sample2_R2.fastq.gz
					    /Sample1_I1.fastq.gz
					    ...
				    /Sample2
					    /Sample2_R1.fastq.gz
                                            /Sample2_R2.fastq.gz
                                            /Sample2_I1.fastq.gz 
```

#### Running the cellranger-atac pipeline
The pipeline is already located on the EFS (/mnt/efs/pipelines/cellranger-atac/) and does NOT need to be cloned from Github on each use.
Simply connect to the front-end [instructions here](https://github.com/sekalylab/cellranger-atac/blob/main/docs/running-on-aws.md) and launch the pipeline using the master script. 


```bash
python cellranger-atac_master.py --help  

Required arguments:  
-i;--input = [i]nput location of files to transfer: can be a S3 bucket or a local absolute path on the EFS (required))  
-o; --output = [o]utput S3 bucket for file cleanup (required)  
-e;--email = [e]mail for notifications of pipeline status

Optional arguments:
-r; --reference = [r]eference for alignment. Defaults to 'GRCh38'. Choices are 'GRCh38' and 'mm10'
-n;--name = [n]ame for run. Will be used to produce files with a distinctive name. Otherwise a generic name will be made
--noaggregate = Deactivate the aggregation portion of the pipeline. Aggregation is performed by default.
--normalize = Normalization mode for aggregation step. Choices are 'depth' and 'none'; default is 'depth'. 
--keep = Does not delete the files on the EFS after run completion. 
--reanalyze_params = Provide a customized parameter csv file for the reanalyze portion of the pipeline. 
```
By default, the pipeline will aggregate ALL cells, but will perform differential enrichment on 100k cells as specified in the [params file](https://github.com/sekalylab/cellranger-atac/blob/main/docs/reanalyze_parameters.csv). If you wish to further tailor the secondary analysis, provide your own csv file as defined in the documentation of [cellranger-atac reanalyze](https://support.10xgenomics.com/single-cell-atac/software/pipelines/latest/using/reanalyze)

Example call :

```bash 
cd /mnt/efs/pipelines/cellranger-atac
python cellranger-atac_master.py \
	 -i s3://patru-emory-genomics-uploads/test-data/ \
	 -o s3://patru-users/userName/test-data \
	 -e slim.fourati@emory.edu \
	 -r GRCh38 \
	 -n Ashish_p123456

```
#### Special parameters
If you need to make a call that uses the more niche parameters (memory, count parameters, etc), you can still clone/copy the whole git repository to another directory, modify those bash scripts accordingly and launch it from there. I would recommend you use the --keep flag just in case.
 

## Outputs
The S3 output location will contain a subdirectory for each data type, with nested directories per sample.
- raw_matrix
- filtered_matrix
- BED
- BAM
- summary (and logs)
- fragments
- Loupe files
- single-cell CSVs
- The output of the Aggregate Call

This structure makes it easy to then transfer locally one file type without downloading all irrelevant files.

e.g. To obtain filtered h5 matrices, you would then, locally, use TKI coupled with the command

```bash 
aws s3 sync s3://patru-user-data/Adam/my-project-outputs/filtered_matrix/ localdirectory/projectX/filtered_matrix
``` 



