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

import json
import boto3
from botocore.exceptions import ClientError
import time
from datetime import datetime

dynamodb = boto3.resource("dynamodb")
cf_client = boto3.client("cloudformation")
stackname = "DdbPermissionsLabStack"
table_name = "batch_processing_one"

try:
    response = cf_client.describe_stacks(StackName=stackname)
    outputs = response["Stacks"][0]["Outputs"]
    for output in outputs:
        keyName = output["OutputKey"]
        if keyName == "PermissionsTableName":
            print(output["OutputValue"])
            table_name = output["OutputValue"]
except ClientError:
    print("You need to run cdk deploy first to get the stack deployed.")

start_program = time.time()
if table_name:
    table = dynamodb.Table(table_name)

    customers = []

    with open("base_transportation_2.json", "r") as file:
        customers = json.load(file)

    with table.batch_writer() as batch:
        counter = 0
        batches = 0
        seconds = 0
        start = time.time()

        # To simulate traffic you can update this loop to 10
        # 5 will take 930 seconds with ramp-up or 300 with on demand tables

        for loop in range(5):
            for item in customers:
                record = {}
                record["PK"] = item["user_name"]
                record["SK"] = "#ROOT#"
                record["user_name"] = item["user_name"]
                record["first_name"] = item["first_name"]
                record["last_name"] = item["last_name"]
                record["email"] = item["email"]
                record["address"] = item["address"]
                batch.put_item(Item=record)
                counter += 1

                if counter % 25 == 0:
                    batches += 1
                    end = time.time()
                    timediff = 1 - (end - start)
                    start = time.time()
                    if seconds < 180 and batches % 4 == 0:
                        print(
                            f"Less than 3 mins - Batch of 100 sleeping for {timediff} seconds"
                        )
                        time.sleep(timediff)
                        seconds += 1
                    elif seconds < 360 and batches % 8 == 0:
                        print(
                            f"Less than 6 mins - Batch of 100 sleeping for {timediff} seconds"
                        )
                        time.sleep(timediff)
                        seconds += 1
                    elif seconds < 540 and batches % 12 == 0:
                        print(
                            f"Less than 9 mins - Batch of 100 sleeping for {timediff} seconds"
                        )
                        time.sleep(timediff)
                        seconds += 1

                if counter % 100 == 0:
                    right_now = datetime.now().isoformat()
                    print(
                        f"{counter} - A batch of 100 records have been processed {right_now}"
                    )

end_program = time.time()
print("Program completed in %s", end_program - start_program)
