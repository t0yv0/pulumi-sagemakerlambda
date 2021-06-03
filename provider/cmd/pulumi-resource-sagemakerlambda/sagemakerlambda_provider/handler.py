"""AWS Lambda script that wraps a SageMaker predict endpoint in a
friendlier interface.

Specifically it accepts JSON objects labelled by the features, and
returns the predicted dependent variable. To do this it needs to know
the column names of the features; this metadata is not currently
retained by SageMaker Model and Endpoint objects.

Environment variables:

    SAGEMAKER_ENDPOINT_NAME - name of the predictor SageMaker endpoint
    SCHEMA_BUCKET           - name of the bucket where the schema object lives
    SCHEMA_KEY              - key of the schema object

Example schema object (first column assumed to be a dependent variable):

    {
        "columns": [
           "quality",
           "fixed acidity",
           "volatile acidity",
           "citric acid": 0.0,
        ]
    }

"""

import boto3
import json
import os


SAGEMAKER_ENDPOINT_NAME = os.environ['SAGEMAKER_ENDPOINT_NAME']
SCHEMA_BUCKET = os.environ['SCHEMA_BUCKET']
SCHEMA_KEY = os.environ['SCHEMA_KEY']
AWS_REGION = os.environ['AWS_REGION']


def load_column_names():
    try:
        resp = s3_client.get_object(Bucket=SCHEMA_BUCKET,
                                    Key=SCHEMA_KEY)
        return json.load(resp['Body'])['columns']
    except Exception as ex:
        raise Exception('Failure while doing s3_client(region={}).get_object(Bucket={}, Key={}): {}'.format(
            AWS_REGION, SCHEMA_BUCKET, SCHEMA_KEY, ex))


sagemaker_client = boto3.client('sagemaker-runtime', region_name=AWS_REGION)
s3_client = boto3.client('s3', region_name=AWS_REGION)
column_names = load_column_names()


def convert_json_request_to_csv(json_req, column_names):
    out = []

    for c in column_names:

        if c not in json_req:
            raise Exception(f'Missing required column: {c}')

        v = json_req[c]

        if not (type(v) == int or type(v) == float):
            raise Exception(f'Value of column {c} must be numeric, got {type(v)}')

        out.append(str(v))

    return ','.join(out)


def predict(csv_payload):
    response = sagemaker_client.invoke_endpoint(
        EndpointName=SAGEMAKER_ENDPOINT_NAME,
        ContentType='text/csv',
        Accept='text/json',
        Body=csv_payload)

    return json.load(response['Body'])


def lambda_handler(event, context):
    csv = convert_json_request_to_csv(event, column_names[1:])
    resp = predict(csv)
    score = resp['predictions'][0]['score']
    return {
        'prediction': {
            column_names[0]: score
        }
    }


if __name__ == '__main__':
    test_datum = {
        "fixed acidity": 7.8,
        "volatile acidity": 0.88,
        "citric acid": 0.0,
        "residual sugar": 2.6,
        "chlorides": 0.098,
        "free sulfur dioxide": 25.0,
        "total sulfur dioxide": 67.0,
        "density": 0.9968,
        "pH": 3.2,
        "sulphates": 0.68,
        "alcohol": 9.8
    }

    print(lambda_handler(test_datum, None))
