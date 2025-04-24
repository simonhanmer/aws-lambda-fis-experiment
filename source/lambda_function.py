#! /usr/bin/env python
import boto3
import os
import logging


# define a logger using logging library. If LOG_LEVEL is not set, default to INFO.
# otherwise use value of LOG_LEVEL
logger = logging.getLogger()
logger.setLevel(os.getenv('LOG_LEVEL', 'INFO'))


# define a lambda_handler function that takes in an event and a context
def lambda_handler(event, context):
    logger.info("Hello from Lambda!")

    # create a new boto3 client for the service 's3'
    s3 = boto3.client('s3')
    # generate a list of all the buckets in the account
    response = s3.list_buckets()

    for bucket in response['Buckets']:
        if bucket['Name'].startswith('aws-'):
            # if the bucket name starts with 'aws-', skip it
            continue
        logger.info(f"Bucket: {bucket['Name']}")

    return ({
        "statusCode": 200,
        "body": "All OK"
    })


# if this file is run directly, run the lambda_handler function with dummy event and context
if __name__ == '__main__':
    lambda_handler(None, None)
