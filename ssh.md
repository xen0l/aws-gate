aws-gate ssh usage:


1) aws-gate ssh
   - directly spawn SSH command from the console, no need to run 'ssh' and configure ssh_config
   - generate and upload ssh key to EC2 instance connect and connect to the instance over SM transport

   Examples:
    aws-gate ssh -p glovoapp -r eu-west-1 -l ec2-user -P 22 -t rsa -b 2048 hostname
    aws-gate ssh -p glovoapp -r eu-west-1 hostname
    aws-gate ssh -l ec2-user hostname
    aws-gate ssh -P 222 hostname

2) aws-gate ssh-proxy
   - replacement for awscli ssm start-session
3) aws-gate ssh-config
    - generate ssh_config based on AWS regions and profiles available