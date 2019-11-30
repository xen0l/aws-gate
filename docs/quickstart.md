# Prerequisites

* Python 3.5+ (earlier Python 3 versions should work too)
* session-plugin-manager from AWS
* Up to date version of SSM Agent must be installed on EC2 instances we want to connect to
* Proper IAM permissions for instance profile

# Installation via pip

_aws-gate_ is available on PyPI:

```
pip install aws-gate
```

## Installation via Homebrew

_aws-gate_ package is available for macOS via Homebrew:

```
brew tap xen0l/homebrew-taps
brew install aws-gate
```

## Installation via Docker

_aws-gate_ is also available as a Docker container via []Github Package Registry](https://github.com/xen0l/aws-gate/packages/):

```
docker pull docker.pkg.github.com/xen0l/aws-gate/aws-gate:latest
```

However, before you are able to download the Docker container, you need to generate a personal token and grant it the following scopes:

* repo
* packages:read

After you have a personal token generated, you will have have to log in to a Github Package Docker registry:

```
docker login docker.pkg.github.com -u $YOUR_GH_USERNAME -p $GH_TOKEN
```

**NOTE: be careful that executing this command in your shell might store your token in your shell history!**

### Executing aws-gate as Docker container

When executing _aws-gate_ as Docker container, we have to pass some additional arguments, so it can find _aws-gate_ configuration as well AWS credentials/config file (~/.aws):

```
docker run --rm -it -v $HOME/.aws-gate/config:/root/.aws-gate/config \
                    -v $HOME/.aws-gate/config.d:/root/.aws-gate/config.d \
                    -v $HOME/.aws:/root/.aws \
                    docker.pkg.github.com/xen0l/aws-gate/aws-gate:latest session ssm-test
```

**Docker container comes with session-manager-plugin pre-downloaded, so you don't have to worry about it.**

## Downloading session-manager-plugin

macOS users can use _aws-gate_ directly to fetch session-manager-plugin. _aws-gate_ will automatically install it (no sudo privileges required). To do so, just run

```
aws-gate bootstrap
```

On Linux platforms, you need to follow official AWS documentation:

* [RPM](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-install-plugin.html#install-plugin-linux)
* [DEB for Ubuntu server](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-install-plugin.html#install-plugin-debian)

In the future, _session-manager-plugin_ bootstrap support on Linux is planned.

## Updating session-manager-plugin

_sesion-manager-plugin_ can be updated via _aws-gate_ itself:

```
aws-gate bootstrap -f
```

## EC2 Instance IAM profile configuration

In order to use SSM, EC2 instance has to use IAM profile with the **AmazonSSMManagedInstanceCore**  managed policy attached or custom policy with similar permissions.

## Ephemeral SSH key support

When using SSH ProxyCommand support, _aws-gate_ always generates ephemeral SSH key in _~/.aws-gate/key_. Then this SSH key is uploaded to the EC2 Instance metadata via [SendSSHPublicKey](https://docs.aws.amazon.com/ec2-instance-connect/latest/APIReference/API_SendSSHPublicKey.html) API function (feature of [EC2 Instance Connect](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/Connect-using-EC2-Instance-Connect.html)). This means that on your EC2 instance, you need to have EC2 Instance Connect working (as simple as installing one package). Follow the instructions [here](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-connect-set-up.html#ec2-instance-connect-install).

## Minimal IAM permissions for uploading ephemeral SSH keys

When using _aws-gate_, ensure that you have the following permissions (replace $REGION and $ACCOUNTID with correct values):

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2-instance-connect:SendSSHPublicKey"
            ],
            "Resource": [
                "arn:aws:ec2:$REGION:$ACCOUNTID:instance/*"
            ],
            "Condition": {
                "StringEquals": {
                    "ec2:osuser": "ec2-user"
                }
            }
        }
    ]
}
```

I recommend creating a custom IAM policy and attaching it to your IAM role.
