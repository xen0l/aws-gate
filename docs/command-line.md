# bootstrap

Download and install session-manager-plugin

```
usage: aws-gate bootstrap [-h] [-f]

optional arguments:
  -h, --help   show this help message and exit
  -f, --force  Forces bootstrap operation
```

# session

Open new session on instance and connect to it

```
usage: aws-gate session [-h] [-p PROFILE] [-r REGION] instance_name

positional arguments:
  instance_name         Instance we wish to open session to

optional arguments:
  -h, --help            show this help message and exit
  -p PROFILE, --profile PROFILE
                        AWS profile to use
  -r REGION, --region REGION
                        AWS region to use
```

# ssh

Open new SSH session on instance and connect to it

```
usage: aws-gate ssh [-h] [-p PROFILE] [-r REGION] [-l OS_USER] [-P PORT]
                    instance_name ...

positional arguments:
  instance_name         Instance we wish to open session to
  command               command to execute on the instance

optional arguments:
  -h, --help            show this help message and exit
  -p PROFILE, --profile PROFILE
                        AWS profile to use
  -r REGION, --region REGION
                        AWS region to use
  -l OS_USER, --os-user OS_USER
                        SSH user to use
  -P PORT, --port PORT  SSH port to use
```

# ssh-config

Generate SSH configuration file

```
usage: aws-gate ssh-config [-h] [-p PROFILE] [-r REGION] [-l OS_USER]
                           [-P PORT]

optional arguments:
  -h, --help            show this help message and exit
  -p PROFILE, --profile PROFILE
                        AWS profile to use
  -r REGION, --region REGION
                        AWS region to use
  -l OS_USER, --os-user OS_USER
                        SSH user to use
  -P PORT, --port PORT  SSH port to use
```

# ssh-proxy

Open new SSH proxy session to instance

```
usage: aws-gate ssh-proxy [-h] [-p PROFILE] [-r REGION] [-l OS_USER] [-P PORT]
                          instance_name

positional arguments:
  instance_name         Instance we wish to open session to

optional arguments:
  -h, --help            show this help message and exit
  -p PROFILE, --profile PROFILE
                        AWS profile to use
  -r REGION, --region REGION
                        AWS region to use
  -l OS_USER, --os-user OS_USER
                        SSH user to use
  -P PORT, --port PORT  SSH port to use
```

# list (ls)

List available instances

```
  -h, --help            show this help message and exit
  -p PROFILE, --profile PROFILE
                        AWS profile to use
  -r REGION, --region REGION
                        AWS region to use
```