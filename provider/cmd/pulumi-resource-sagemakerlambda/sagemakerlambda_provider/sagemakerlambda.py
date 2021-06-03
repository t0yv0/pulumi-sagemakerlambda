# Copyright 2016-2021, Pulumi Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import pathlib

from typing import Optional, List

from pulumi_aws import sagemaker, iam, kms, lambda_, s3
import pulumi
import pulumi_aws as aws
import sagemaker as real_sagemaker


class SagemakerPredictorLambdaArgs:

    model_data_bucket: pulumi.Input[str]
    """ID of a bucket where trained model data is stored."""

    model_data_key: Optional[pulumi.Input[str]]
    """Key of the trained model S3 object in model_data_bucket. If this is
    None, provisioning goes only as far as it can without a trained
    model."""

    column_names: pulumi.Input[List[str]]
    """Column names of the features, to map named to positional. For
    regression predictors, the first column is assumed to be the
    dependent variable."""

    initial_instance_count: pulumi.Input[int]
    """Initial number of instances to power the SageMaker predict endpoint. Defaults to 1."""

    instance_type: pulumi.Input[str]
    """Type of instance to power the SageMaker predict endpoint. Defaults to the smallest instance."""

    region: pulumi.Input[str]
    """AWS region name. If None, infer from the environment."""

    account_id: pulumi.Input[str]
    """AWS account ID."""

    model_image: pulumi.Input[str]
    """Custom Docker image for serving the model in the SageMaker
    endpoint. If this is omitted, model_framework must be
    specified."""

    model_framework: Optional[pulumi.Input[str]]
    """Built-in SageMaker framework such as `linear-learner`. If this is
    given, model_image should not be given as the code will find the
    right image automatically. """

    def __init__(self,
                 model_data_bucket: pulumi.Input[str],
                 column_names: pulumi.Input[List[str]],
                 model_data_key: Optional[pulumi.Input[str]] = None,
                 initial_instance_count: Optional[pulumi.Input[int]] = None,
                 instance_type:Optional[pulumi.Input[str]] = None,
                 region: Optional[pulumi.Input[str]] = None,
                 account_id: Optional[pulumi.Input[str]] = None,
                 model_image: Optional[pulumi.Input[str]] = None,
                 model_framework: Optional[pulumi.Input[str]] = None) -> None:

        if initial_instance_count is None:
            initial_instance_count = 1

        self.initial_instance_count = initial_instance_count

        if instance_type is None:
            instance_type = 'ml.t2.medium'

        self.instance_type = instance_type

        self.column_names = column_names

        if region is not None:
            self.region = region
        else:
            self.region = aws.get_region().name

        if account_id is not None:
            self.account_id = account_id
        else:
            self.account_id = aws.get_caller_identity().account_id

        if model_image is not None:
            self.model_image = model_image
        else:
            if model_framework is not None:
                self.model_image = pulumi.Output.from_input(model_framework).apply(
                    lambda f: pulumi.Output.from_input(self.region).apply(
                        lambda r: real_sagemaker.image_uris.retrieve(framework=f, region=r)))
            else:
                raise Exception('model_framework is required when model_image is unspecified')

        self.model_data_bucket = pulumi.Output.from_input(model_data_bucket)
        self.model_data_key = pulumi.Output.from_input(model_data_key) if model_data_key is not None else None


    @staticmethod
    def from_inputs(inputs: pulumi.Inputs) -> 'SagemakerPredictorLambdaArgs':
        """This boilerplate will be automated in the future."""

        return SagemakerPredictorLambdaArgs(
            model_data_bucket=inputs['modelDataBucket'],
            column_names=inputs['columnNames'],
            model_data_key=inputs.get('modelDataKey', None),
            initial_instance_count=inputs.get('initialInstanceCount', None),
            instance_type=inputs.get('instanceType', None),
            region=inputs.get('region', None),
            account_id=inputs.get('accountId', None),
            model_image=inputs.get('modelImage', None),
            model_framework=inputs.get('modelFramework', None)
        )


class SagemakerPredictorLambda(pulumi.ComponentResource):

    training_role_arn: pulumi.Output[str]
    """ARN of the provisioned role that can be reused for model training."""

    endpoint_name: Optional[pulumi.Output[str]]
    """Name of the provisioned SageMaker endpoint."""

    lambda_function_name: Optional[pulumi.Output[str]]
    """Name of the provisioned Lambda function."""


    def __init__(self,
                 name: str,
                 args: SagemakerPredictorLambdaArgs,
                 props: Optional[dict] = None,
                 opts: Optional[pulumi.ResourceOptions] = None) -> None:

        super().__init__('pkg:index:SagemakerPredictorLambda', name, props, opts)

        account_id = args.account_id
        region = args.region

        kms_key = kms.Key(
            f'{name}-kms-key',
            deletion_window_in_days=30,
            opts=pulumi.ResourceOptions(parent=self)
        )

        lambda_role = iam.Role(
            f'{name}-lambda-role',
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
                    name=f'{name}-lambda-role-policy',
                    policy=pulumi.Output.from_input(args.model_data_bucket).apply(lambda bucket: json.dumps({
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
            ],
            opts=pulumi.ResourceOptions(parent=self)
        )

        # TODO we are currently lumping the role used by training scirpt and
        # the role used by Model (execution_role) into one. They can be
        # segregated and tightened up.
        #
        # TODO tighten kms and sagemaker perms.
        role = iam.Role(
            f'{name}-role',
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

            inline_policies=pulumi.Output.from_input(args.model_data_bucket).apply(lambda bucket: [
                iam.RoleInlinePolicyArgs(
                    name=f'{name}-policy',
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
            ]),

            opts=pulumi.ResourceOptions(parent=self)
        )

        self.training_role_arn = role.arn

        # Resources below this line need a trained model.
        if args.model_data_key is not None:
            self._continue_init(name, args, args.model_data_key,
                                role=role,
                                lambda_role=lambda_role,
                                kms_key=kms_key)
        else:
            self.endpoint_name = None
            self.lambda_function_name = None
            return

    def _continue_init(self,
                       name: str,
                       args: SagemakerPredictorLambdaArgs,
                       model_data_key: pulumi.Input[str],
                       kms_key: kms.Key,
                       role: iam.Role,
                       lambda_role: iam.Role) -> None:

        model = sagemaker.Model(
            f'{name}-model',
            execution_role_arn=role.arn,
            primary_container=sagemaker.ModelPrimaryContainerArgs(
                image=args.model_image,
                model_data_url=pulumi.Output.from_input(args.model_data_bucket).apply(
                    lambda b: pulumi.Output.from_input(model_data_key).apply(
                        lambda k: f's3://{b}/{k}'))
            ),
            opts=pulumi.ResourceOptions(parent=self)
        )

        endpoint_config = sagemaker.EndpointConfiguration(
            f'{name}-endpoint-config',
            production_variants=[
                sagemaker.EndpointConfigurationProductionVariantArgs(
                    variant_name='AllTraffic',
                    model_name=model.name,
                    initial_instance_count=args.initial_instance_count,
                    initial_variant_weight=1,
                    instance_type=args.instance_type,
                ),
            ],
            kms_key_arn=kms_key.arn,
            opts=pulumi.ResourceOptions(parent=self)
        )

        endpoint = sagemaker.Endpoint(
            f'{name}-endpoint',
            endpoint_config_name = endpoint_config.name,
            opts=pulumi.ResourceOptions(parent=self)
        )

        policy = aws.iam.Policy(
            f'{name}-invoke-policy',
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
            })),
            opts=pulumi.ResourceOptions(parent=self)
        )

        schema_object_path = f'schema/{name}.json'
        schema_object = s3.BucketObject(
            schema_object_path,
            source=pulumi.StringAsset(json.dumps({
                'columns': args.column_names
            })),
            key=schema_object_path,
            bucket=args.model_data_bucket,
            opts=pulumi.ResourceOptions(parent=self)
        )

        lambda_function = lambda_.Function(
            f'{name}-lambda',
            timeout=30,
            role=lambda_role.arn,
            runtime='python3.8',
            handler='handler.lambda_handler',
            code=pulumi.AssetArchive({
                'handler.py': pulumi.FileAsset(pathlib.Path(__file__).absolute().parent.joinpath('./handler.py'))
            }),
            environment=lambda_.FunctionEnvironmentArgs(variables={
                'SAGEMAKER_ENDPOINT_NAME': endpoint.name,
                'SCHEMA_BUCKET': args.model_data_bucket,
                'SCHEMA_KEY': schema_object.key
            }),
            opts=pulumi.ResourceOptions(parent=self)
        )

        iam.PolicyAttachment(
            f'{name}-invoke-policy-attachment',
            roles=[lambda_role.name],
            policy_arn=policy.arn,
            opts=pulumi.ResourceOptions(parent=self)
        )

        self.lambda_function_name = lambda_function.name
        self.endpoint_name = endpoint.name
