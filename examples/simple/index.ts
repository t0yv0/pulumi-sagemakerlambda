import * as sl from "@pulumi/sagemakerlambda";
import * as aws from "@pulumi/aws";

const bucket = new aws.s3.Bucket("winequality-model");


const slambda = new sl.SagemakerPredictorLambda("s-lambda", {
    modelDataBucket: bucket.id,
    columnNames: ['a', 'b', 'c'],
    modelDataKey: 'nope',
    initialInstanceCount: 1,
    instanceType: 'whatever',
    region: 'us-east-1',
    accountId: 'account-id-whatever',
    modelImage: 'image-whatever',
    modelFramework: 'linear-learner'
});

export const trainingRoleArn = slambda.trainingRoleArn;
export const endpointName = slambda.endpointName;
export const lambdaFunctionName = slambda.lambdaFunctionName;


// export const bucket = page.bucket;
// export const url = page.websiteUrl;
