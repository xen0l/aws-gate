0.8.7 (2020-02-12)
------------------

* Improve instance listing performance in cases when there are many instances connecged to AWS Systems Manager 

0.8.6 (2020-01-17)
------------------

* Extend user agent with aws-gate version information, so it can be easier tracked in CloudTrail

0.8.5 (2020-01-14)
------------------

* Provide more debug output when fetching host information from config files. 

0.8.4 (2019-12-24)
------------------

* Version 0.8.3 introduced a bug into querying instance by autoscaling group, where the name would not be properly parsed. This is now fixed.

0.8.3 (2019-12-23)
------------------

* aws-gate now supports querying instances via **asg** identifier
* Querying instances by autoscaling group tag is now fixed

0.8.2 (2019-12-11)
------------------

* aws-gate now ships with Bash completion

0.8.1 (2019-12-10)
------------------

* _plugin\_required_ decorator now also checks for the presence of system-installed session-manager-plugin (contribution by [@kit494way](https://github.com/kit494way))
 
0.8.0 (2019-12-03)
------------------

* **list** subcommand is able to return output in multiple formats: JSON, TSV, CSV and human
* aws-gate now ships with ZSH completion

0.7.2 (2019-11-30)
------------------

* Docker container is now available
* Tests have been refactored to use pytest
* aws-gate now uses Github Actions

0.7.1 (2019-11-11)
------------------

* Turn off SSH host key verification in **aws-gate ssh**

0.7.0 (2019-11-09)
------------------

* Add **ssh** command to be able to directly connect to instances via SSH

0.6.1 (2019-10-29)
------------------

* aws-gate will now use AWS profile from AWS_VAULT environment variable when called from aws-vault

0.6.0 (2019-10-11)
------------------

* Add support for Linux in **bootstrap**
* Black coding style is now used
* pre-commit hooks are available for easier development

0.5.0 (2019-10-04)
------------------

* Add **ssh-proxy** command to be able to use ssh over Session Manager session
* Add **ssh-config** command to generate _~/.ssh/config_ configuration for easier integration with _ssh_
* AWS profile_name and region_name validation happens now on all commands

0.4.3 (2019-09-26)
------------------

* Fix problem with uncaptured command output
* bootstrap not working when ~/.aws-gate is missing

0.4.2 (2019-08-21)
------------------

* Use default region and profile in list command
* Always use own version of session-manager-plugin if available
* Improve tests coverage

0.4.1 (2019-08-12)
------------------

* Homebrew package is now available

0.4.0 (2019-08-11)
------------------

* Add **bootstrap**, which downloads session-manager-plugin on macOS
* aws-gate now queries only for running instances
* aws-gate functions using session-manager-plugin are now safeguarded by plugin_required and plugin_version decorators

0.3.0 (2019-05-26)
------------------

* Add support for aws-vault (portions contributed by [@danmx](https://github.com/danmx))
* Option to query by name
* Improve performance of queries by tag
* Add configuration file support


0.2.0 (2019-01-12)
------------------

* Allow opening session via tag identifier (contribution by [@openbankGit](https://github.com/openbankGit))
* Add list subcommand (contribution by [@openbankGit](https://github.com/openbankGit))

0.1.0 (2018-11-18)
-------------------

* Initial release
