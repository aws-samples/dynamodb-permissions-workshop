## Amazon DynamoDB Permissions Workshop Code

Hello and Welcome to the Amazon DynamoDB Permissions workshop, the full step by step workshop can be found on [dynamodb-security-101 workshop](https://www.eventbox.dev/published/lesson/dynamodbs-security-101/security-labs.html) hosted in Event Box.

If you are running this event either using one of the AWS provided accounts or in your own development account we recommend you to use Cloud9.

Once your VM is created start by cloning this repository in the `~/environment` folder and run the [setup step](https://www.eventbox.dev/published/lesson/dynamodbs-security-101/security-labs/security-00.html) to create the required infrastructure and populate the base table that will be used during this workshop.

## CDK Template

The workshop uses CDK code to show the basics of DynamoDB Security. The base version which is the one on the main, will deploy the minimum required infrastructure to run the workshop, which is an Amazon DynamoDB Table, an AWS lambda function and the permissions required to execute the lambda function and read data from the table. That code is avaliable under the [`ddb_permissions_lab`](ddb_permissions_lab) folder the python script [`ddb_permissions_lab_stack.py`](ddb_permissions_lab/ddb_permissions_lab_stack.py).

The `cdk.json` file tells the CDK Toolkit how to execute your app.

This project is set up like a standard Python project. The initialization
process also creates a virtualenv within this project, stored under the `.venv`
directory. To create the virtualenv it assumes that there is a `python3`
(or `python` for Windows) executable in your path with access to the `venv`
package. If for any reason the automatic creation of the virtualenv fails,
you can create the virtualenv manually.

To manually create a virtualenv on MacOS and Linux:

```
$ python3 -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```

To add additional dependencies, for example other CDK libraries, just add
them to your `setup.py` file and rerun the `pip install -r requirements.txt`
command.

## Useful commands

- `cdk ls` list all stacks in the app
- `cdk synth` emits the synthesized CloudFormation template
- `cdk deploy` deploy this stack to your default AWS account/region
- `cdk diff` compare deployed stack with current state
- `cdk docs` open CDK documentation

## Step by Step

The workshop consists of 4 steps and you can find the answer to every step in the [`by_step`](ddb_permissions_lab/by_steps/) folder.

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.
