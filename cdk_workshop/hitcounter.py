from constructs import Construct
from aws_cdk import (
    aws_lambda as _lambda,
    aws_dynamodb as ddb,
)
from aws_cdk import RemovalPolicy

class HitCounter(Construct):

    @property
    def handler(self):
        return self._handler

    # added a property to expose the Lambda function that will be invoked by the API Gateway:
    @property # "expose our table as a property of HitCounter"
    def table(self):
        return self._table

    def __init__(
        self,
        scope: Construct,
        id: str,
        downstream: _lambda.IFunction,
        read_capacity: int = 5, # "added a read_capacity parameter to the constructor"
        **kwargs
        ):
        # "added a check to ensure that read_capacity is between 5 and 20":
        if read_capacity < 5 or read_capacity > 20:
            raise ValueError("readCapacity must be greater than 5 or less than 20")
        
        super().__init__(scope, id, **kwargs)

        self._table = ddb.Table(
            self, 'Hits',
            partition_key={'name': 'path', 'type': ddb.AttributeType.STRING},
            encryption=ddb.TableEncryption.AWS_MANAGED, # use AWS managed encryption for the DynamoDB table
            removal_policy=RemovalPolicy.DESTROY, # (NB) override default behavior of keeping the table when the stack is deleted
            # (NB) "this is not a good idea for production code, but it's ok for our workshop"
            read_capacity=read_capacity, # "set the read capacity of the table to the value passed in the constructor"
        )

        self._handler = _lambda.Function(
            self, 'HitCountHandler',
            runtime=_lambda.Runtime.PYTHON_3_13,
            handler='hitcount.handler',
            code=_lambda.Code.from_asset('lambda'),
            environment={ # ".. wired the Lambda's environment variables to the function_name and table_name of our resources"
                'DOWNSTREAM_FUNCTION_NAME': downstream.function_name,
                'HITS_TABLE_NAME': self._table.table_name,
            }
        )

        self._table.grant_read_write_data(self._handler) # grant the Lambda function permission to read and write to the DynamoDB table
        downstream.grant_invoke(self._handler)     # grant the downstream Lambda function permission to be invoked by the hit counter