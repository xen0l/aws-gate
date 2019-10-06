# Debug mode

_aws-gate_ is written with easy debugging in mind. To activate a debug output, just set **GATE_DEBUG** environment variable
and on the next invocation _aws-gate_ will start producing debug output:

```
% export GATE_DEBUG=1
% aws-gate session ssm-test
2019-05-26 01:18:23,535 - aws_gate.config  - DEBUG - Located config file: /Users/xenol/.aws-gate/config
2019-05-26 01:18:23,538 - aws_gate.utils   - DEBUG - Obtaining boto3 session object
2019-05-26 01:18:23,549 - aws_gate.utils   - DEBUG - Obtained configured AWS profiles: default development preproduction production
2019-05-26 01:18:23,550 - aws_gate.utils   - DEBUG - Obtaining boto3 session object
2019-05-26 01:18:23,560 - aws_gate.utils   - DEBUG - Obtained configured AWS profiles: default development preproduction production
2019-05-26 01:18:23,560 - aws_gate.utils   - DEBUG - Obtaining boto3 session object
2019-05-26 01:18:23,574 - aws_gate.utils   - DEBUG - Obtaining ssm client
2019-05-26 01:18:23,608 - aws_gate.utils   - DEBUG - Obtaining boto3 session object
2019-05-26 01:18:23,636 - aws_gate.utils   - DEBUG - Obtaining ec2 boto3 resource
2019-05-26 01:18:23,694 - aws_gate.query   - DEBUG - Querying EC2 API for instance identifier: ssm-test
2019-05-26 01:18:24,029 - aws_gate.query   - DEBUG - Found 1 maching instances
2019-05-26 01:18:24,030 - aws_gate.query   - DEBUG - Matching instance: i-0772e4c1dcdd763b6
2019-05-26 01:18:24,030 - aws_gate.session - INFO  - Opening session on instance i-0772e4c1dcdd763b6 (eu-west-1) via profile default
2019-05-26 01:18:24,030 - aws_gate.session - DEBUG - Creating a new session on instance: i-0772e4c1dcdd763b6 (eu-west-1)
...
```

# Reporting problems

When you run into a problem with _aws-gate_ or something is not working as described, please do not hesitate and open an issue in the project's [issue tracker](https://github.com/xen0l/aws-gate/issues).