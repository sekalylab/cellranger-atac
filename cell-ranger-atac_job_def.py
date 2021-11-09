
import boto3
import time


# security info
region = "us-east-2"

batch_client = boto3.client('batch', region_name=region)
batch_client.register_job_definition(
    jobDefinitionName="cellranger-atac-job-def-1",
    type="container",
    containerProperties={
        "image": "cumulusprod/cellranger-atac:2.0.0",
        "vcpus": 32,
        "memory": 192000,
        "command": [ "ls", "/mnt"],
        "volumes": [
            {
                "host": {
                    "sourcePath": "/mnt/efs"
                },
                "name": "efs"
            }
        ],
        "mountPoints": [
            {
                "containerPath": "/mnt",
                "readOnly": False,
                "sourceVolume": "efs"
            }
        ]
    }
)
