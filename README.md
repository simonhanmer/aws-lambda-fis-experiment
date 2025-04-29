# aws-lambda-fis-experiment

This repository contains the resources used to build the demo used in my recent presentations around [FIS](https://aws.amazon.com/fis/).

If you have any quesions, feel free to reach out to me via [LinkedIn](https://www.linkedin.com/in/simonhanmer/) or raise an issue, and I'll try and help.

## What we build
The main resources deployed are 

### Lambda infrastructure
* 2 lambda functions - one configured to interact with FIS, with the FIS wrapper and a tag for filtering, and one that won't be triggered by FIS. Both lambdas use the same source code (from the [./source](source)) folder which simply generates a list of S3 buckets in the account
* A IAM Role giving the lambda permissions to execute, and query S3 buckets
* A Cloudwatch Log group for the lambdas

### FIS Infrastructure
* 3 FIS experiment templates:
    * one to introduce a delay in the execution of the lambda
    * one to change the returned status of the lambda to HTTP [418](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/418)
    * one to introduce an error in the execution of the lambda
* 2 S3 Buckets - one used to pass the config between FIS and the Lambda Layer, and one to store the FIS Logs.
* A CloudWatch Log Group - again to store the experiment logs
* An IAM role for use by the experiments - giving permission for FIS to interact with the lambdas, buckets and log groups.


## How to deploy

The [template.yml](./template.yml) file contains a modified CloudFormation template, using the [AWS SAM](https://aws.amazon.com/serverless/sam/) approach to simplify deployment of the lambda.

To deploy the resources used in the demo,
1. Ensure you have an AWS account
1. Install the AWS SAM CLI - as per these [instructions](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html)
1. Make sure you have the CLI configured with appropriate credentials
1. Run `sam build` to generate the appropriate package.
1. Run `sam deploy --guided --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM` and answer the questions - I've provided a  [samconfig.toml](samconfig.toml) file to help with this, but please review the values in the file before using this.

    Once you've deploy the template successfully, you can combine this and the previous step by running `sam build && sam deploy`.

## Reviewing the lambda without a running experiment
Once you have deployed the template, you'll have two lambdas in your account; one with the prefix `test-function` that won't be affected by FIS experiments, and one with the prefix `test-function-with-fis` that is configured to work with the experiment templates in this repository.

To trigger the FIS lambda, navigate to the AWS console, and select the `test-function-with-fis` lambda function. You'll need to add a test event, as described [here](https://docs.aws.amazon.com/lambda/latest/dg/testing-functions.html). With that in place, you can trigger the lambda function and see the results in the console.

In it's standard state (i.e. when there are no experiments running), the lambda will return a successful response looking something like:

``` json
{
  "statusCode": 200,
  "body": "All OK"
}
```

If we look at the CloudWatch logs for the lambda, as well as the normal logs, we'll see a number of lines at the beginning from the FIS lambda layer, indicating the lambda is properly configured.

## Configuring a Lambda for FIS.

To enable a lambda to interact with FIS experiments, we'll need a number of items in place.

1. We'll need to ensure that the lambda is configured to use the FIS layer. This layer is provided by AWS and the arn is available in two SSM parameters under the path `/aws/service/fis/lambda-extension/AWS-FIS-extension*` - one each for x86 and arm respectively.
2. We'll need an S3 bucket to pass information between the lambda and FIS. We'll either need permissions in the lambda execution role or the policy attached to the bucket to allow FIS and the lambda to read and write to the bucket.
3. We need to add two environment variables to the lambda:

    a. `AWS_FIS_CONFIGURATION_LOCATION` should point to the `FISConfigs` prefix within the bucket

    b. `AWS_LAMBDA_EXEC_WRAPPER` should have the value `/opt/aws-fis/bootstrap`

## Testing the lambda with an FIS experiment.
As mentioned earlier, this repository deploys three experiment templates which can be used to test the configured lambda. We can choose any of these to trigger an experiment, by navigating in the console to `AWS FIS > Experiment templates`, selecting a template and then starting an experiment based on the template, either by first selecting a template from the list, or opening one, and then selecting `Start Experiment`.

Once the experiment is started, it will show a status which should soon transition from `Initiating` to `Running`. Each of the experiments should run for 5 minutes, which should be sufficient to open the lambda functions in the console, selecting the `-with-fis` function and invoking it via the test event we created earlier.

With an experiment in progress, we should see the lambda's behaviour being modified based on the template chosen. This should be reflected in the function's output.


