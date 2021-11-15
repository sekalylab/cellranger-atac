## Cellranger-ATAC on Emory AWS

1. Connect to the front end machine 

```bash
ssh -i *userName*.pem *username*@10.65.122.170
```


2a. (OPTIONAL) Add the tki command to your PATH variable  
```bash
nano ~/.bashrc 

## Copy/Paste this line into the file
export PATH=$PATH:/mnt/efs/bin/emory-tki/bin
```
Close the file by pressign CTRL + X, followed by Y.


2. create temporary AWS CLI credentials using TKI
```bash
tki
Username: *emoryUserName*
Password: *emoryPassword*
Available Duo Authentication Methods: 1.auto
Available Regions: 2:us-east-2
```
Accept the push/sms/phone call.
This will create AWS CLI credentials valid for 12h (in $HOME/.aws/credentials).


3. Launch the pipeline
```bash
python /mnt/efs/pipelines/cellranger-atac/cellranger-atac_master.py \
	 -i s3://patru-emory-genomics-uploads/test-data/ \
	 -o s3://patru-users/userName/test-data \
	 -e slim.fourati@emory.edu \
	 -r GRCh38 \
	 -n Ashish_p123456
```

If you decided to either:
1. first upload your raw files to the EFS
2. use the --keep flag to prevent the EFS cleanup after the run

then make sure you empty the EFS as fast as posible to avoid unnecessary charges. 
