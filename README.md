# EC2 Evil Janitor aka EJ
## Overview
Initial functionality allows to Stop/Start or List instances based on requested tags. The intention is to run script through automation pipeline and as temporary workaround use it with scheduler like cron.

The future functionality is:
1. To extend search to more parameters other than tags...
2. Add tagging functionality
3. Add 'Auto-Stop' / 'Auto-Start' tags for further stop/start customization
4. Probably integrate idle detection: https://gist.github.com/chiradeep/6877402a5705c84dd2ac


```
root@avitools:~/evil_janitor# ./ec2_janitor.py -h
usage: ec2_janitor.py [-h] --region REGION [--tag-owner TAG_OWNER]
                      [--tag-key TAG_KEY] [--tag-value TAG_VALUE]
                      [--lab-timezone LAB_TIMEZONE]
                      [--exclude-tag EXCLUDE_TAG] --action ACTION [--apply]

ec2_janitor.py --region us-west-2 --tag-owner Training --apply --action stop

optional arguments:
  -h, --help            show this help message and exit
  --region REGION
  --tag-owner TAG_OWNER
                        Owner Tag Search mask: *tag_owner
  --tag-key TAG_KEY     Custom Tag Search
  --tag-value TAG_VALUE
                        Custom Tag Search
  --lab-timezone LAB_TIMEZONE
                        Supported lab timezones: EST, PST, GMT, SGT
  --exclude-tag EXCLUDE_TAG
                        Exclude from action based on tag
  --action ACTION       Supported actions: stop, start or list
  --apply               Apply changes
```
## Examples
### List all training instances
```
root@avitools:~/evil_janitor# ./ec2_janitor.py --region us-east-1 --tag-owner='Training' --action list
us-east-1 EC2 Resources state at 2019-03-24 08:49:11.526070
aviGSLBdev-Training_jumpbox i-09bace244d0a037d6 running t2.medium
dns_server1 i-09172fd2408505148 stopped t2.medium
server4 i-08a0d74029c1f67fe stopped t2.medium
server3 i-0b4eb8872e424926d stopped t2.medium
server1 i-0c27450e404e92670 stopped t2.medium
dns_server2 i-02c8a741563ec6783 stopped t2.medium
server2 i-0af2fdfa320f47f3b stopped t2.medium
aviGSLBdev-Training_student1_controller i-03fb81fa9add48e13 stopped c4.2xlarg
```
### List all training instances delivered in EST
```
root@avitools:~/evil_janitor# ./ec2_janitor.py --region us-east-1 --tag-owner='Training' --action list --lab-timezone EST
Lab Timezone: EST
us-east-1 EC2 Resources state at 2019-03-24 08:49:41.170925
aviGSLBdev-Training_jumpbox i-09bace244d0a037d6 running t2.medium
dns_server1 i-09172fd2408505148 stopped t2.medium
server4 i-08a0d74029c1f67fe stopped t2.medium
server3 i-0b4eb8872e424926d stopped t2.medium
server1 i-0c27450e404e92670 stopped t2.medium
dns_server2 i-02c8a741563ec6783 stopped t2.medium
server2 i-0af2fdfa320f47f3b stopped t2.medium
aviGSLBdev-Training_student1_controller i-03fb81fa9add48e13 stopped c4.2xlarge
```

### Stop instances (Dry-Run) delivered in EST and exclude instances with tag Lab_Noshut
Check the current state before applying
```
root@avitools:/opt/avi/ansible/workspace/scripts/python/aws# ./ec2_janitor.py --region ca-central-1 --tag-owner='Training' --lab-timezone EST --exclude-tag Lab_Noshut --action stop 
Time: 2019-03-06 22:35:21.120889
EC2 Resources to be stopped at  2019-03-06 22:35:21.120889
Stopping Instances List:  []
```
The already stopped instances will not be shown.
### Stop instances (Apply)
Without --apply flag the changes won't be applied.
```
root@avitools:/opt/avi/ansible/workspace/scripts/python/aws# ./ec2_janitor.py --region ca-central-1 --tag-owner='Training' --action stop --lab-timezone EST --exclude-tag Lab_Noshut --action stop --apply
Time: 2019-03-06 22:39:30.204697
EC2 Resources to be stopped at  2019-03-06 22:39:30.204697
unnamed i-0010f8e1c40d139df
Stopping Instances List:  ['i-0010f8e1c40d139df']
```
### List or check the current state
```
root@avitools:/opt/avi/ansible/workspace/scripts/python/aws# ./ec2_janitor.py --region ca-central-1 --tag-owner='Training' --action list
EC2 Resources state at  2019-03-06 22:40:07.828738
test1 i-0e91f4aff52a92862 stopped t2.micro
unnamed i-0010f8e1c40d139df stopped t2.micro
```
### Start instances (Dry-Run)
```
root@avitools:/opt/avi/ansible/workspace/scripts/python/aws# ./ec2_janitor.py --region ca-central-1 --tag-owner='Training' --action start
EC2 Resources to be started at  2019-03-06 22:40:30.879422
test1 i-0e91f4aff52a92862
unnamed i-0010f8e1c40d139df
Starting Instances List: ['i-0e91f4aff52a92862', 'i-0010f8e1c40d139df']
```
### Start instances (Apply)
```
root@avitools:/opt/avi/ansible/workspace/scripts/python/aws# ./ec2_janitor.py --region ca-central-1 --tag-owner='Training' --action start --apply
EC2 Resources to be started at  2019-03-06 22:40:53.705902
test1 i-0e91f4aff52a92862
unnamed i-0010f8e1c40d139df
Starting Instances List: ['i-0e91f4aff52a92862', 'i-0010f8e1c40d139df']
```
### List or check the current state
```
root@avitools:/opt/avi/ansible/workspace/scripts/python/aws# ./ec2_janitor.py --region ca-central-1 --tag-owner='Training' --action list
EC2 Resources state at  2019-03-06 22:41:15.290966
test1 i-0e91f4aff52a92862 running t2.micro
unnamed i-0010f8e1c40d139df running t2.micro
```
