# aws-gate
[![Build Status](https://travis-ci.org/xen0l/aws-gate.svg?branch=master)](https://travis-ci.org/xen0l/aws-gate)[![codecov](https://codecov.io/gh/xen0l/aws-gate/branch/master/graph/badge.svg)](https://codecov.io/gh/xen0l/aws-gate)[![Codacy Badge](https://api.codacy.com/project/badge/Grade/5f4385e925e34788a20e40b4a3319b2d)](https://app.codacy.com/app/xen0l/aws-gate?utm_source=github.com&utm_medium=referral&utm_content=xen0l/aws-gate&utm_campaign=Badge_Grade_Settings)[![PyPI version](https://badge.fury.io/py/aws-gate.svg)](https://badge.fury.io/py/aws-gate)


aws-gate is a AWS SSM Session Manager CLI client. It aims to provide richer user experience than official tooling.

## Features

* Opening AWS SSM session from CLI
* [session-manager-plugin](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-install-plugin.html) bootstrapping
* Querying instances by different instance identifiers
* config and config.d support
* SSH ProxyCommand support (allows to use ssh and scp over AWS SSM session)
* SSH client support to open SSH sessions directly (convenient wrapper around _ssh_)
* Docker container support

## Motivation

It is a very common and recommend security practice to run a bastion host if you want to connect to your workload in AWS.
However, running bastion host has its own issues:

* maintaining additional instance which requires patching/updating
* SSH key management and distribution (SSH CA works nicely, but it still has to be owned by somebody)
* exposing SSH port to the network (ideally you want to have this behind a VPN or open only to trusted IPs, which can be seen as an anti-pattern in the cloud)

To address some of these issues, Amazon released a service while ago to fix this - [AWS Systems Manager Session Manager](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager.html). However, CLI user experience of Session Manager is limited and lacks some features:

* ability to connect to instances by other means (e.g. DNS, IP, tag, instance name, autoscaling group) as aws cli supports only connecting by instance IDs
* configuration file support for storing connection information via Session Manager

Out of the frustration with these problems, _aws-gate_ was born.
