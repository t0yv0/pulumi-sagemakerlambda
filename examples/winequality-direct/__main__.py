import json
import pathlib
import pulumi
import pulumi_aws as aws
from pulumi_aws import s3, kms, iam, sagemaker, lambda_
import sagemaker as real_sagemaker


# Config

MODEL_FRAMEWORK='linear-learner'
INITIAL_INSTANCE_COUNT = 1
INSTANCE_TYPE = 'ml.t2.medium'

COLUMN_NAMES = [
    "quality",
    "fixed acidity",
    "volatile acidity",
    "citric acid",
    "residual sugar",
    "chlorides",
    "free sulfur dioxide",
    "total sulfur dioxide",
    "density",
    "pH",
    "sulphates",
    "alcohol"
]


cfg = pulumi.Config()
trained_model_key = cfg.get('trained_model_key') or None

region = aws.get_region().name
account_id = aws.get_caller_identity().account_id
model_image = real_sagemaker.image_uris.retrieve(framework=MODEL_FRAMEWORK, region=region)


# Resources


model_data_bucket = s3.Bucket('my-model-data')


kms_key = kms.Key(
    'my-kms-key',
    deletion_window_in_days=30
)


lambda_role = iam.Role(
    'my-lambda-role',
    assume_role_policy=json.dumps({
        'Version': '2012-10-17',
        'Statement': [
            {
                'Action': 'sts:AssumeRole',
                'Effect': 'Allow',
                'Principal': {
                    'Service': 'lambda.amazonaws.com'
                }
            }
        ],
    }),
    inline_policies=[
        iam.RoleInlinePolicyArgs(
            name=f'my-lambda-role-policy',
            policy=model_data_bucket.id.apply(lambda bucket: json.dumps({
                'Version': '2012-10-17',
                'Statement': [
                    {
                        'Action': [
                            's3:GetObject',
                            's3:ListBucket'
                        ],
                        'Effect': 'Allow',
                        'Resource': [
                            f'arn:aws:s3:::{bucket}',
                            f'arn:aws:s3:::{bucket}/*',
                        ]
                    },
                    {
                        'Action': [
                            'logs:CreateLogGroup',
                            'logs:CreateLogStream',
                            'logs:PutLogEvents'
                        ],
                        'Effect': 'Allow',
                        'Resource': f'arn:aws:{region}:{account_id}:log-group:/aws/lambda/*'
                    }
                ],
            })
        ))
    ]
)


role = iam.Role(
    'my-role',
    assume_role_policy=json.dumps({
        'Version': '2012-10-17',
        'Statement': [
            {
                'Action': 'sts:AssumeRole',
                'Effect': 'Allow',
                'Principal': {
                    'Service': 'sagemaker.amazonaws.com'
                }
            }
        ],
    }),
    inline_policies=model_data_bucket.id.apply(lambda bucket: [
        iam.RoleInlinePolicyArgs(
            name='my-inline-policy',
            policy=json.dumps({
                'Version': '2012-10-17',
                'Statement': [
                    {
                        'Action': [
                        's3:GetObject',
                            's3:PutObject',
                            's3:DeleteObject',
                            's3:ListBucket'
                        ],
                        'Effect': 'Allow',
                        'Resource': [
                            f'arn:aws:s3:::{bucket}',
                            f'arn:aws:s3:::{bucket}/*',
                        ]
                    },
                    {
                        'Action': [
                            'logs:CreateLogGroup',
                            'logs:CreateLogStream',
                            'logs:DescribeLogStreams',
                            'logs:GetLogEvents',
                            'logs:PutLogEvents'
                        ],
                        'Effect': 'Allow',
                        'Resource': f'arn:aws:logs:{region}:{account_id}:log-group:/aws/sagemaker/*'
                    },
                    {
                        'Action': [
                            'sagemaker:CreateTrainingJob',
                            'sagemaker:DescribeTrainingJob',
                        ],
                        'Effect': 'Allow',
                        'Resource': f'arn:aws:sagemaker:{region}:{account_id}:*'
                    },
                    {
                        'Action': [
                            'kms:Encrypt',
                            'kms:Decrypt',
                            'kms:ReEncrypt*',
                            'kms:GenerateDataKey*',
                            'kms:DescribeKey'
                        ],
                        'Effect': 'Allow',
                        'Resource': f'arn:aws:kms:{region}:{account_id}:*'
                    },
                ]
            }))
    ])
)


if trained_model_key is not None:

    model = sagemaker.Model(
        'my-model',
        execution_role_arn=role.arn,
        primary_container=sagemaker.ModelPrimaryContainerArgs(
            image=model_image,
            model_data_url=model_data_bucket.id.apply(
                lambda bucket: f's3://{bucket}/{trained_model_key}')
        )
    )


    endpoint_config = sagemaker.EndpointConfiguration(
        'my-endpoint-config',
        production_variants=[
            sagemaker.EndpointConfigurationProductionVariantArgs(
                variant_name='AllTraffic',
                model_name=model.name,
                initial_instance_count=INITIAL_INSTANCE_COUNT,
                initial_variant_weight=1,
                instance_type=INSTANCE_TYPE,
            ),
        ],
        kms_key_arn=kms_key.arn
    )


    endpoint = sagemaker.Endpoint(
        'my-endpoint',
        endpoint_config_name = endpoint_config.name
    )


    policy = iam.Policy(
        'my-invoke-policy',
        policy=endpoint.arn.apply(lambda sagemaker_endpoint_arn: json.dumps({
            'Version': '2012-10-17',
            'Statement': [
                {
                    'Action': [
                        'sagemaker:InvokeEndpoint'
                    ],
                    'Effect': 'Allow',
                    'Resource': sagemaker_endpoint_arn
                }
            ],
        }))
    )


    schema_object_path = f'schema/my.json'


    schema_object = s3.BucketObject(
        schema_object_path,
        source=pulumi.StringAsset(json.dumps({
            'columns': COLUMN_NAMES
        })),
        key=schema_object_path,
        bucket=model_data_bucket
    )


    lambda_function = lambda_.Function(
        'my-lambda',
        timeout=30,
        role=lambda_role.arn,
        runtime='python3.8',
        handler='handler.lambda_handler',
        code=pulumi.AssetArchive({
            'handler.py': pulumi.FileAsset(pathlib.Path(__file__).absolute().parent.joinpath('./handler.py'))
        }),
        environment=lambda_.FunctionEnvironmentArgs(variables={
            'SAGEMAKER_ENDPOINT_NAME': endpoint.name,
            'SCHEMA_BUCKET': model_data_bucket,
            'SCHEMA_KEY': schema_object.key
        })
    )

    iam.PolicyAttachment(
        'my-invoke-policy-attachment',
        roles=[lambda_role.name],
        policy_arn=policy.arn,
    )

    pulumi.export('lambda_function_name', lambda_function.name)

pulumi.export('bucket', model_data_bucket.id)
pulumi.export('kms_key_id', kms_key.id)
pulumi.export('training_role_arn', role.arn)
