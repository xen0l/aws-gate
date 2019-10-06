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

