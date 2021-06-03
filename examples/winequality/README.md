# winequality

This example stands up a Lambda function to predict red wine quality
from features such as pH, density and acidity, based on P. Cortez et
al (2009) dataset. The focus is on infrastructure and not machine
learning here, so everything is kept as simple as possible:

- no feature transformation, direct CSV input data

- model training using `linear-learner` built into SageMaker


## Prepare infra

First we provision a bucket for the model and setup basic roles and
permissions:

```
$ pulumi up
```


## Prepare features

Run the following script:

```
$ python dataprep.py
```

Raw wine quality data is copied to S3 with minimal modification,
adapting it to SageMaker format:

- headers are stripped

- the dependent variable `quality` is placed in the first column

In a realistic scenario you would could be doing feature engineering
here instead.


## Training

We will train a `linear-learner` model in the cloud. Note that this
will create a `Training Job` object in SageMaker, which currently
persists forever. These objects are not currently managed by Pulumi,
so we use straight `boto3` code to do the training.

```
$ python train.py
```

Allow 4-5 minutes for this to complete.

When done, you will find the trained model output to S3:

```
$ aws s3 ls --recursive $(pulumi stack output bucket)
2021-06-03 17:15:42        913 trained_models/train-linear-learner-winequality-2021-06-03-2112/output/model.tar.gz
2021-06-03 17:12:20        195 training_data/_schema.json
2021-06-03 17:12:19      23203 training_data/csv/part_c0.csv.gz
```

We can now instruct Pulumi which model we want to deploy:

```
$ pulumi config set trained_model_key trained_models/train-linear-learner-winequality-2021-06-03-2112/output/model.tar.gz
```


## Model serving

We can now provision our prediction (model serving) endpoint:

```
$ pulumi up
```

Allow 10-15 minutes for this to complete.

We can now query the model for predictions by invoking our lambda. Try
the included script:

```
$ python invoke_lambda.py
{
 "lambda": "winequality-predictor-lambda-2f2a6c4",
 "request": {
  "alcohol": 9.8,
  "chlorides": 0.098,
  "citric acid": 0.0,
  "density": 0.9968,
  "fixed acidity": 7.8,
  "free sulfur dioxide": 25.0,
  "pH": 3.2,
  "residual sugar": 2.6,
  "sulphates": 0.68,
  "total sulfur dioxide": 67.0,
  "volatile acidity": 0.88
 },
 "response": {
  "prediction": {
   "quality": 4.9622802734375
  }
 }
}
```

Note how having a Lambda layer let us simplify the raw SageMaker
Endpoint interface by adding awareness of column names. In a realistic
scenario this can also be used to do authentication, logging and other
functions not specific to ML.

While not yet covered in this example, building a REST endpoint
powered by the lambda function is possible with
[API-Gateway](https://aws.amazon.com/api-gateway/).


## Cleanup

Do not forget to `pulumi desroy` to avoid idle infra charges.
