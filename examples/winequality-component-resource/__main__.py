import pulumi
from pulumi_aws import s3, kms
import sagemakerlambda


# Config

MODEL_FRAMEWORK='linear-learner'

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


# Resources


model_data_bucket = s3.Bucket('my-model-data')


predictor_lambda = sagemakerlambda.SagemakerPredictorLambda(
    'winequality-predictor',
    args=sagemakerlambda.SagemakerPredictorLambdaArgs(
        model_framework=MODEL_FRAMEWORK,
        model_data_bucket=model_data_bucket.id,
        model_data_key=trained_model_key,
        column_names=COLUMN_NAMES))


kms_key = kms.Key('winequality-model-training-key', deletion_window_in_days=30)


# Exports


pulumi.export('bucket', model_data_bucket.id)
pulumi.export('lambda_function_name', predictor_lambda.lambda_function_name)
pulumi.export('endpoint_name', predictor_lambda.endpoint_name)
pulumi.export('training_role_arn', predictor_lambda.training_role_arn)
pulumi.export('kms_key_id', kms_key.id)
