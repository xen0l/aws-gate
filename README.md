# aws-gate
[![Build Status](https://travis-ci.org/xen0l/aws-gate.svg?branch=master)](https://travis-ci.org/xen0l/aws-gate)[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)[![codecov](https://codecov.io/gh/xen0l/aws-gate/branch/master/graph/badge.svg)](https://codecov.io/gh/xen0l/aws-gate)[![Codacy Badge](https://api.codacy.com/project/badge/Grade/5f4385e925e34788a20e40b4a3319b2d)](https://app.codacy.com/app/xen0l/aws-gate?utm_source=github.com&utm_medium=referral&utm_content=xen0l/aws-gate&utm_campaign=Badge_Grade_Settings)[![PyPI version](https://badge.fury.io/py/aws-gate.svg)](https://badge.fury.io/py/aws-gate)![PyPI - Downloads](https://img.shields.io/pypi/dm/aws-gate)

AWS SSM Session manager client

[Documentation](https://aws-gate.readthedocs.io)

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

or via Docker

```
docker login docker.pkg.github.com -u $YOUR_GH_USERNAME -p $GH_TOKEN
docker pull docker.pkg.github.com/xen0l/aws-gate/aws-gate:latest
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
aws-gate session 172.31.35.113
```

* tags
```
aws-gate session Name:SSM-test
```

* name (uses tag identifier under the hood)
```
aws-gate session SSM-test
```

* autoscaling group name (uses tag identifier under the hood)
```
aws-gate session asg:dummy-v001
```

#### SSH ProxyCommand support

AWS SSM Session Manager supports tunneling SSH sessions over it. Moreover, _aws-gate_ supports generating ephemeral SSH
keys and uploading them via EC2 Instance Connect API. However, to use this functionality,
EC2 Instance Connect [setup](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-connect-set-up.html) is needed.

To use this functionality, simply run **aws-gate ssh-config**, which will generate the required _~/.ssh/config_ snippet for you:
```
% aws-gate ssh-config
Host *.eu-west-1.default
IdentityFile /Users/xenol/.aws-gate/key
IdentitiesOnly yes
User ec2-user
Port 22
ProxyCommand sh -c "aws-gate ssh-proxy -p `echo %h | sed -Ee 's/^(.*)\.(.*)\.(.*)$/\\3/g'` -r `echo %h | sed -Ee 's/^(.*)\.(.*)\.(.*)$/\\2/g'` `echo %h | sed -Ee 's/^(.*)\.(.*)\.(.*)$/\\1/g'`"
```

Store the snippet inside __~/.ssh/config_:
```
% aws-gate ssh-config >> ~/.ssh/config
```

Then connect via *ssh*:
```
% ssh ssm-test.eu-west-1.default
Last login: Fri Oct  4 17:17:02 2019 from localhost

       __|  __|_  )
       _|  (     /   Amazon Linux 2 AMI
      ___|\___|___|

https://aws.amazon.com/amazon-linux-2/
1 package(s) needed for security, out of 20 available
Run "sudo yum update" to apply all updates.
[ec2-user@ip-172-31-35-173 ~]$
```

SSH session to instance _ssm-test_ in eu-west-1 AWS region via _default_ AWS profile is opened.

#### SSH support

*aws-gate* provides a way to open SSH session on the instance directly. This is achieved by wrapping around _ssh_ under the hood.
Simply run **aws-gate ssh <instance_identifier>**:

```
% aws-gate ssh ssm-test
Last login: Sat Nov  9 10:23:11 2019 from localhost

       __|  __|_  )
       _|  (     /   Amazon Linux 2 AMI
      ___|\___|___|

https://aws.amazon.com/amazon-linux-2/
28 package(s) needed for security, out of 56 available
Run "sudo yum update" to apply all updates.
[ec2-user@ip-172-31-35-173 ~]$
```

If you wish to execute a specific command (or plug it into your shell pipelines):

```
% aws-gate ssh ssm-test uname -a
Linux ip-172-31-35-173.eu-west-1.compute.internal 4.14.123-111.109.amzn2.x86_64 #1 SMP Mon Jun 10 19:37:57 UTC 2019 x86_64 x86_64 x86_64 GNU/Linux
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
