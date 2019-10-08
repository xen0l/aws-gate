# Configuration file

If you are oftne connecting to the same instances, it might be handy to store the configuration inside the configuration file,
so you don't have to retype the same command all over again._aws-gate_ supports storing instance connection information in a dedicated config file located at _~/.aws-gate/config_. THe format of the configuraiton file is as follows:


```
hosts:
  - alias: webapp-dev
    name: webapp-dev
    profile: profile-dev
    region: eu-west-2
  - alias: webapp-pre
    name: webapp-pre
    profile: profile-pre
    region: eu-west-2
  - alias: webapp-pro
    name: webapp-pro
    profile: profile-pro
    region: eu-west-2
defaults:
  profile: profile-dev
  region: eu-west-1
```

**hosts** dictionary holds information how to connect to the EC2 instance and which attributes to use. Based on the example above, the following works:

```
aws-gate session webapp-pre
```
**defaults** dictionary holds default configuration for profile and region, when these are not provided.

# config.d support

_aws-gate_ will automatically load condiguration from _~/.aws-gate/config.d_. This is especially useful is you need to share you configuration within your team or you are working on multiple projects.