# aws-gate
[![Build Status](https://travis-ci.org/xen0l/aws-gate.svg?branch=master)](https://travis-ci.org/xen0l/aws-gate)[![codecov](https://codecov.io/gh/xen0l/aws-gate/branch/master/graph/badge.svg)](https://codecov.io/gh/xen0l/aws-gate)[![Codacy Badge](https://api.codacy.com/project/badge/Grade/5f4385e925e34788a20e40b4a3319b2d)](https://app.codacy.com/app/xen0l/aws-gate?utm_source=github.com&utm_medium=referral&utm_content=xen0l/aws-gate&utm_campaign=Badge_Grade_Settings)[![PyPI version](https://badge.fury.io/py/aws-gate.svg)](https://badge.fury.io/py/aws-gate)

AWS SSM Session manager client

## Motivation

I am using AWS a lot and I am tired of dealing with everything that comes with the bastion host (additional instance one has to maintain, distribute SSH keys (shared SSH keys are not an option for me), exposing SSH to the network). A while ago, Amazon released a service to fix this - [AWS Systems Manager Session Manager](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager.html). However, CLI user experience of Session Manager is limited and lacks some features:

* ability to connect to instances by other means (e.g. DNS, IP, tag, instance name, autoscaling group) as aws cli supports only connecting by instance IDs
* configuration file support for storing connection information via Session Manager

*aws-gate* tries to address these issues.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

* Python 3.5+ (earlier Python 3 versions should work too)
* [session-plugin-manager](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-install-plugin.html) from AWS
* SSM Agent version 2.3.68.0 or later must be installed on EC2 instances we want to connect to
* Proper IAM permissions for instance profile

### Installing

```
pip install aws-gate
```

or via Homebrew

```
brew tap xen0l/homebrew-taps
brew install aws-gate
```

### Features

#### config and config.d support

You can store information about to connect to your instance (name, region and profile) and *aws-gate* will do everything for you. The config file is stored in **~/.aws-gate/config** and has the following YAML syntax:

```
hosts:
  - alias: backend-pre
    name: backend
    profile: preproduction
    region: eu-west-1
  - alias: backend-pro
    name: backend
    profile: production
    region: eu-west-1

defaults:
  profile: development
  region: eu-west-1
```

where *hosts* stores connection information and *defaults* default configuration settings to use. To connect to instance _backend-pre_, execute:
```
aws-gate session backend-pre
```

You can place additional configuration files in **~/.aws-gate/config.d**. This is ideal when you are working on different projects or when you need to share configuration inside your team.

#### Querying instances by different instance identifiers

*aws-gate* supports querying for instances with following identifiers:

* instance id
```
aws-gate session i-0772e4c1dcdd763b6
```
* DNS name
```
aws-gate session ec2-34-245-174-132.eu-west-1.compute.amazonaws.com
```
* private DNS name
```
aws-gate session ip-172-31-35-113.eu-west-1.compute.internal
```

* IP address
```
aws-gate session 34.245.174.13
```

* private IP address
```
aws-gate sssion 172.31.35.113
```

* tags
```
aws-gate session Name:SSM-test
```

* name (uses tag identifier under the hood)
```
aws-gate session SSM-tes
```

## Debugging mode

If you run into issues, you can get detailed debug log by setting **GATE_DEBUG** environment variable:
```
export GATE_DEBUG=1
```

After setting the environment variable, the debug mode will be automatically enabled:
```
% aws-gate session test
2019-05-26 01:18:23,535 - aws_gate.config  - DEBUG - Located config file: /Users/xenol/.aws-gate/config
2019-05-26 01:18:23,538 - aws_gate.utils   - DEBUG - Obtaining boto3 session object
2019-05-26 01:18:23,549 - aws_gate.utils   - DEBUG - Obtained configured AWS profiles: default development preproduction production
2019-05-26 01:18:23,550 - aws_gate.utils   - DEBUG - Obtaining boto3 session object
2019-05-26 01:18:23,560 - aws_gate.utils   - DEBUG - Obtained configured AWS profiles: default development preproduction production
2019-05-26 01:18:23,560 - aws_gate.utils   - DEBUG - Obtaining boto3 session object
2019-05-26 01:18:23,574 - aws_gate.utils   - DEBUG - Obtaining ssm client
2019-05-26 01:18:23,608 - aws_gate.utils   - DEBUG - Obtaining boto3 session object
2019-05-26 01:18:23,636 - aws_gate.utils   - DEBUG - Obtaining ec2 boto3 resource
2019-05-26 01:18:23,694 - aws_gate.query   - DEBUG - Querying EC2 API for instance identifier: SSM-test
2019-05-26 01:18:24,029 - aws_gate.query   - DEBUG - Found 1 maching instances
2019-05-26 01:18:24,030 - aws_gate.query   - DEBUG - Matching instance: i-0772e4c1dcdd763b6
2019-05-26 01:18:24,030 - aws_gate.session - INFO  - Opening session on instance i-0772e4c1dcdd763b6 (eu-west-1) via profile default
2019-05-26 01:18:24,030 - aws_gate.session - DEBUG - Creating a new session on instance: i-0772e4c1dcdd763b6 (eu-west-1)
...
```

Debug mode also enables printing of Python stack traces if there is a crash or some other problem.

## License

This project is licensed under the BSD License - see the [LICENSE.md](LICENSE.md) file for details
