from pulumi_aws import s3
import pulumi
import pulumi_sagemakerlambda as spl


cfg = pulumi.Config()

bucket = s3.Bucket('winequality-model')

trained_model_key = cfg.get('trained_model_key') or None

predictor_lambda = spl.SagemakerPredictorLambda(
    'winequality-predictor',
    args=spl.SagemakerPredictorLambdaArgs(
        model_framework='linear-learner',
        model_data_bucket=bucket.id,
        model_data_key=trained_model_key,
        column_names=[
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
        ]))


pulumi.export('bucket', bucket.id)

pulumi.export('lambda_function_name', predictor_lambda.lambda_function_name)

pulumi.export('endpoint_name', predictor_lambda.endpoint_name)

pulumi.export('training_role_arn', predictor_lambda.training_role_arn)
