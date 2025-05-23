from constructs import Construct
from aws_cdk import (
    aws_lambda as _lambda,
    aws_dynamodb as ddb,
)

class HitCounter(Construct):

    @property
    def handler(self):
        return self._handler    

    def __init__(self, scope: Construct, id: str, downstream: _lambda.IFunction, **kwargs):
        super().__init__(scope, id, **kwargs)

        table = ddb.Table(
            self, 'Hits',
            partition_key={'name': 'path', 'type': ddb.AttributeType.STRING}
        )

        self._handler = _lambda.Function(
            self, 'HitCountHandler',
            runtime=_lambda.Runtime.PYTHON_3_13,
            handler='hitcount.handler',
            code=_lambda.Code.from_asset('lambda'),
            environment={ # ".. wired the Lambda's environment variables to the function_name and table_name of our resources"
                'DOWNSTREAM_FUNCTION_NAME': downstream.function_name,
                'HITS_TABLE_NAME': table.table_name,
            }
        )

        table.grant_read_write_data(self._handler) # grant the Lambda function permission to read and write to the DynamoDB table
        downstream.grant_invoke(self._handler)     # grant the downstream Lambda function permission to be invoked by the hit counter