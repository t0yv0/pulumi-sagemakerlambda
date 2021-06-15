import boto3
import json
import subprocess as sp

test_datum = {
    "fixed acidity": 7.8,
    "volatile acidity": 0.88,
    "pH": 3.2,
    "citric acid": 0.0,
    "residual sugar": 2.6,
    "chlorides": 0.098,
    "free sulfur dioxide": 25.0,
    "total sulfur dioxide": 67.0,
    "density": 0.9968,
    "sulphates": 0.68,
    "alcohol": 9.8 * 2
}


pulumi_config = json.loads(sp.check_output('pulumi config --json', shell=True).decode().strip())
region = pulumi_config['aws:region']['value']
pulumi_stack_output = json.loads(sp.check_output('pulumi stack output --json', shell=True).decode().strip())
lambda_client = boto3.client('lambda', region_name=region)
sagemaker_wrapper_function_name = pulumi_stack_output['lambda_function_name']

response = lambda_client.invoke(
    FunctionName=sagemaker_wrapper_function_name,
    Payload=json.dumps(test_datum).encode())


out = json.load(response['Payload'])

print(json.dumps({'lambda': sagemaker_wrapper_function_name,
                  'request': test_datum,
                  'response': out}, indent=True, sort_keys=True))
