"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
Permission is hereby granted, free of charge, to any person obtaining a copy of this
software and associated documentation files (the "Software"), to deal in the Software
without restriction, including without limitation the rights to use, copy, modify,
merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from aws_cdk import (
    Aspects,
    Duration,
    Stack,
    CfnOutput,
    RemovalPolicy,
    aws_lambda as _lambda,
    aws_dynamodb as dynamodb,
    aws_iam as iam,
    aws_kinesis as kinesis,
)

# import cdk_nag
import json

from aws_solutions_constructs.aws_lambda_dynamodb import (
    LambdaToDynamoDBProps,
    LambdaToDynamoDB,
)
from constructs import Construct


class DdbPermissionsLabStack(Stack):
    def _create_ddb_table(self):
        my_stream = kinesis.Stream(self, "MyDDBStreamKinesis")
        dynamodb_table = dynamodb.Table(
            self,
            "PermissionsTable",
            partition_key=dynamodb.Attribute(
                name="PK", type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(name="SK", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            stream=dynamodb.StreamViewType.NEW_AND_OLD_IMAGES,
            kinesis_stream=my_stream,
            removal_policy=RemovalPolicy.DESTROY,
        )

        CfnOutput(self, "PermissionsTableName", value=dynamodb_table.table_name)

        return dynamodb_table

    # def _set_ddb_trigger_function(self, ddb_table):
    #     async_lambda = _lambda.Function(
    #         self,
    #         "AsyncHandler",
    #         runtime=_lambda.Runtime.PYTHON_3_9,
    #         code=_lambda.Code.from_asset("asycn_lambda"),
    #         handler="app.handler",
    #         environment={
    #             "APP_TABLE_NAME": ddb_table.table_name,
    #         },
    #     )

    def _scan_lambda(self, ddb_table):

        scan_lambda = _lambda.Function(
            self,
            "ScanLambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("src/scan_lambda"),
            handler="app.handler",
            environment={
                "DDB_TABLE_NAME": ddb_table.table_name,
            },
            timeout=Duration.seconds(300),
        )

        ddb_table.grant_read_write_data(scan_lambda)

        dynamodb_policy = iam.Policy(
            self,
            "ddb-policy",
            statements=[
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    resources=[ddb_table.table_arn],
                    actions=["dynamodb:Query"],
                    conditions={
                        "ForAllValues:StringEquals": {
                            "dynamodb:Attributes": [
                                "PK",
                                "SK",
                                "trip_id",
                                "user_name",
                                "status",
                                "date_time",
                            ]
                        },
                        "StringEqualsIfExists": {
                            "dynamodb:Select": "SPECIFIC_ATTRIBUTES"
                        },
                    },
                ),
                iam.PolicyStatement(
                    effect=iam.Effect.DENY,
                    resources=[ddb_table.table_arn],
                    actions=["dynamodb:*"],
                    conditions={
                        "StringNotEquals": {"aws:sourceVpce": "vpce-0f8a24fe67a37dad5"}
                    },
                ),
            ],
        )

        scan_lambda.role.attach_inline_policy(dynamodb_policy)

        # Activating DynamoDB Streams
        ddb_table.grant_read_write_data(scan_lambda)
        ddb_table.grant_stream_read(scan_lambda)

        company_inserts = _lambda.CfnEventSourceMapping(
            scope=self,
            id="rideEvents",
            function_name=scan_lambda.function_name,
            event_source_arn=ddb_table.table_stream_arn,
            maximum_batching_window_in_seconds=5,
            starting_position="LATEST",
            batch_size=5,
        )

        company_inserts.add_property_override(
            property_path="FilterCriteria",
            value={
                "Filters": [
                    {
                        "Pattern": json.dumps(
                            {
                                "eventName": ["INSERT", "MODIFY"],
                                "dynamodb": {
                                    "NewImage": {
                                        "SK": {"S": [{"prefix": "#ROOT#"}]},
                                    }
                                },
                            }
                        )
                    }
                ]
            },
        )

        return scan_lambda

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Creates a DynamoDB Table
        ddb_table = self._create_ddb_table()
        self._scan_lambda(ddb_table)

        code_in_vpc = LambdaToDynamoDB(
            self,
            "LambdaInsideVPC",
            lambda_function_props=_lambda.FunctionProps(
                runtime=_lambda.Runtime.PYTHON_3_9,
                code=_lambda.Code.from_asset("src/vpc_lambda"),
                handler="app.handler",
                environment={
                    "DDB_TABLE_NAME": ddb_table.table_name,
                    "STREAM_ARN": ddb_table.table_stream_arn,
                },
                timeout=Duration.seconds(30),
            ),
            existing_table_obj=ddb_table,
            deploy_vpc=True,
        )

        ddb_table.grant_stream_read(code_in_vpc.lambda_function)

        inserts_in_vpc = _lambda.CfnEventSourceMapping(
            scope=self,
            id="rideeventsVpc",
            function_name=code_in_vpc.lambda_function.function_name,
            event_source_arn=ddb_table.table_stream_arn,
            maximum_batching_window_in_seconds=1,
            starting_position="LATEST",
            batch_size=1,
        )
        # CDK NAG
        # Aspects.of(self).add(cdk_nag.AwsSolutionsChecks())
