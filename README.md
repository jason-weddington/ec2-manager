**EC2 Manager Script***

This simple script can list, start, and stop EC2 instances on your AWS account. The script requires that AWS credentials are already set up as described here:
https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html

Usage:
  ec2_manager.py (--list | --start INSTANCE | --stop INSTANCE) [ --quiet | --verbose] [--test]
Options:
  -h --help                 Show this screen.
  -v --version              Show version.
  -l --list                 Lists all registered EC2 instances in the user's account.
  --start=INSTANCE          Start an EC2 instance
  --stop=INSTANCE           Stop an EC2 instance
  --test                    Runs the program in test mode to check permissions. Does not stop or start instances.
  --quiet                   Print less text
  --verbose                 Print more text
  
Example:

'''
$ ec2_manager --list
Instances found in your AWS account:

i-1234
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  Type:        g4dn.4xlarge
  Private IP:  1.2.3.4
  Public IP:   1.2.3.4
  State:       stopped


i-1234
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  Type:        g4dn.xlarge
  Private IP:  1.2.3.4
  Public IP:   1.2.3.4
  State:       stopped

$ ec2_manager --start i-1234
$ ec2_manager --stop i-1234
'''
