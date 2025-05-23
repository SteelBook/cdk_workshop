import json
import os

import boto3

ddb = boto3.resource('dynamodb')
table = ddb.Table(os.environ['HITS_TABLE_NAME']) # name of the DynamoDB table; (NB) "decided when we deploy our app"
_lambda = boto3.client('lambda')


def handler(event, context):
    print('request: {}'.format(json.dumps(event)))
    table.update_item(
        Key={'path': event['path']},
        UpdateExpression='ADD hits :incr',
        ExpressionAttributeValues={':incr': 1}
    )

    resp = _lambda.invoke(
        FunctionName=os.environ['DOWNSTREAM_FUNCTION_NAME'], # (NB) "decided when we deploy our app"
        Payload=json.dumps(event),
    )

    body = resp['Payload'].read()

    print('downstream response: {}'.format(body))
    return json.loads(body)
