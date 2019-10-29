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
