# aws-gate

AWS SSM Session manager client

## Motivation

I am using AWS a lot and I am tired of dealing with everything that comes with the bastion host (additional instance one has to maintain, distribute SSH keys (shared SSH keys are not an option for me), exposing SSH to the network). A while ago, Amazon released a service to fix this - [AWS Systems Manager Session Manager](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager.html). However, CLI user experience of Session Manager is limited and lacks some features:

* ability to connect to instances by other means (e.g. DNS, IP, tag, instance name, autoscaling group) as aws cli supports only connecting by instance IDs
* configuration file support for storing connection information via Session Manager

*aws-gate* tries to address these issues.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

* Python 3.7+ (earlier Python 3 versions should work too)
* [session-plugin-manager](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-install-plugin.html) from AWS
* SSM Agent version 2.3.68.0 or later must be installed on EC2 instances we want to connect to
* Proper IAM permissions for instance profile

### Installing

```
pip install aws-gate
```

## License

This project is licensed under the BSD License - see the [LICENSE.md](LICENSE.md) file for details