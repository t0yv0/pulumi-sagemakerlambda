"""Starts a linear learner AWS SageMaker training job. Note that
training job objects are retained forever and never deleted on
SageMaker. Discover jobs with `aws sagemaker list-training-jobs`.

Note that training normally takes 4-5 minutes.

"""

import boto3
import datetime
import json
import sagemaker
import smart_open
import subprocess as sp
import sys


pulumi_config = json.loads(sp.check_output('pulumi config --json', shell=True).decode().strip())
pulumi_stack_output = json.loads(sp.check_output('pulumi stack output --json', shell=True).decode().strip())

region = pulumi_config['aws:region']['value']
bucket = pulumi_stack_output['bucket']
kms_key_id = pulumi_stack_output['kms_key_id']
training_role_arn = pulumi_stack_output['training_role_arn']

training_data_source = f's3://{bucket}/training_data/csv'
trained_model_outputs = f's3://{bucket}/trained_models'
schema = f's3://{bucket}/training_data/_schema.json'

training_image = sagemaker.image_uris.retrieve(framework='linear-learner', region=region)

client = boto3.client('sagemaker', region_name=region)


def read_attribute_names():
    with smart_open.open(schema, 'r') as fp:
        return json.load(fp)['columns']


attribute_names = read_attribute_names()
now_label = datetime.datetime.utcnow().strftime('%Y-%m-%d-%H%M')

job = client.create_training_job(
    TrainingJobName=f'train-linear-learner-winequality-{now_label}',
    AlgorithmSpecification={
        'TrainingImage': training_image,
        'TrainingInputMode': 'File'
    },
    ResourceConfig={
        'InstanceType': 'ml.m5.large',
        'InstanceCount': 1,
        'VolumeSizeInGB': 16,
        'VolumeKmsKeyId': kms_key_id
    },
    HyperParameters={
        'predictor_type': 'regressor'
    },
    RoleArn=training_role_arn,
    InputDataConfig=[
        {
            'ChannelName': 'train',
            'ContentType': 'text/csv',
            'InputMode': 'File',
            'DataSource': {
                'S3DataSource': {
                    'S3DataType': 'S3Prefix',
                    'S3Uri': training_data_source,
                    'AttributeNames': attribute_names
                },
            },
        }
    ],
    OutputDataConfig={
        'KmsKeyId': kms_key_id,
        'S3OutputPath': trained_model_outputs
    },
    StoppingCondition={
        'MaxRuntimeInSeconds': 600,
        'MaxWaitTimeInSeconds': 600
    },
    RetryStrategy={
        'MaximumRetryAttempts': 2
    }
)

print(job)
