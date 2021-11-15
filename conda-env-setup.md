## AWS pipeline conda environment install

#### Goal 
Add the conda environment to the PATH variable to access all required dependencies for running Boto3 dependent pipelines.

This is a once per user setup.

#### Steps
1. Login the front end node by first navigating to the directory where you stored your SSH *userName*.pem key and runnign the following command:

```bash
ssh -i *userName*.pem *username*@10.65.122.170
```
2. Modify your ~/.bashrc file to add the conda environment to your PATH:


```bash
## Open file
nano ~/.bashrc


## copy / paste following lines (until the end of the chunk!)


# >>> conda initialize >>>
# !! Contents within this block are managed by 'conda init' !!
__conda_setup="$('/home/ec2-user/miniconda3/bin/conda' 'shell.bash' 'hook' 2> /dev/null)"
if [ $? -eq 0 ]; then
    eval "$__conda_setup"
else
    if [ -f "/home/ec2-user/miniconda3/etc/profile.d/conda.sh" ]; then
        . "/home/ec2-user/miniconda3/etc/profile.d/conda.sh"
    else
        export PATH="/home/ec2-user/miniconda3/bin:$PATH"
    fi
fi
unset __conda_setup
# <<< conda initialize <<<

```
Close the file	by using CTRL +	X , followed by	Y to confirm changes.

3. Exit	the front end node and relog to	it to apply changes.


4. if everything worked	correctly, your	command	line prompt should have switched from


```bash
[your-user-name@ip-10-65-122-170 efs]$
```

to

```bash
(base) [your-user-name@ip-10-65-122-170 efs]$
```


