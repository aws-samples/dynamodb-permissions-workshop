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

import os
import boto3
import json
from botocore.exceptions import ClientError

dynamodb = boto3.resource("dynamodb")
dynamodb_table = dynamodb.Table(os.environ.get("DDB_TABLE_NAME", ""))
dynamodb_client = boto3.client("dynamodb")
streams = boto3.client("dynamodbstreams")


def scan_table():
    try:
        response = dynamodb_client.scan(
            TableName=os.environ.get("DDB_TABLE_NAME", ""),
        )
        return response
    except ClientError as e:
        """
        If there is an error it means this is the first product of this category
        Set the product value instead of in crement
        """
        print(f"something went wrong {e}")


def query_user(user_name):
    items = dynamodb_client.query(
        TableName=os.environ.get("DDB_TABLE_NAME", ""),
        KeyConditionExpression="#pk = :pk and begins_with(#sk, :sk)",
        ExpressionAttributeNames={"#pk": "PK", "#sk": "SK"},
        ExpressionAttributeValues={
            ":pk": {"S": f"{user_name}"},
            ":sk": {"S": "COMPLETED"},
        },
    )["Items"]
    return items


def handler(event, context):
    print("We have received this event:")
    print(event)

    # stream_data = streams.describe_stream(StreamArn=os.environ.get("STREAM_ARN", ""))
    results = {}

    print("This is the stream information")
    # print(json.dumps(stream_data))

    # results = scan_table()
    # results = query_user("lastley98")
    print(json.dumps(results))
    return {"result": results}
