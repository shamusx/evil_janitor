#!/usr/bin/python
import argparse
import boto3
import datetime
import json
import requests


def send_message(message,type='text'):
    webhook_url = ''
    if type == 'title':
        slack_message = {"text": message }
    else:
        slack_message = {"attachments": [{"text":message }]}
    r = requests.post(webhook_url, data=json.dumps(slack_message), headers={'Content-Type': 'application/json'})
    if r.status_code != 200:
        raise ValueError('Request to slack returned an error %s, the response is:\n%s' % (r.status_code, r.text))


def stop_instances(region, filters, exclude_tag, apply=False):
    current_time = datetime.datetime.utcnow()
    stop_instance_ids = []
    stop_instances = {}
    stop_instances['noname'] = []
    ec2 = boto3.client('ec2',region_name=region)
    ec2_instances = ec2.describe_instances(Filters=filters)
    print region, 'EC2 resources to be stopped at', current_time
    for reservation in ec2_instances["Reservations"]:
        for instance in reservation["Instances"]:
            if instance['State']['Name'] == 'running' and exclude_tag not in str(instance):
                stop_instance_ids.append(instance['InstanceId'])
                name_tag_exists = False
                try:
                  if instance['Tags']:
                      for tag in instance['Tags']:
                        if tag['Key'] == 'Name' and tag['Value'] != '':
                          print tag['Value'], instance['InstanceId']
                          stop_instances[tag['Value']] = instance['InstanceId']
                          name_tag_exists = True
                      if name_tag_exists == False:
                          print 'noname', instance['InstanceId']
                          stop_instances['noname'].append(instance['InstanceId'])
                except:
                  pass
    print 'Stopping Instances List: ', stop_instance_ids
    if stop_instances['noname'] == []:
        stop_instances.pop('noname')
    if stop_instances:
        send_message('*' + region + ' EC2 resources to be stopped at ' + str(current_time) +  '*', type='title')
        send_message(str(stop_instances))
        send_message('_' +  str(args) + '_', type='title')
        send_message('\r')
    if apply and stop_instance_ids:
        ec2.stop_instances(InstanceIds=stop_instance_ids)


def start_instances(region, filters, exclude_tag, apply=False):
    current_time = datetime.datetime.utcnow()
    start_instance_ids = []
    start_instances = {}
    start_instances['noname'] = []
    ec2 = boto3.client('ec2',region_name=region)
    ec2_instances = ec2.describe_instances(Filters=filters)
    print region, 'EC2 Resources to be started at', current_time
    for reservation in ec2_instances["Reservations"]:
        for instance in reservation["Instances"]:
            if instance['State']['Name'] == 'stopped' and exclude_tag not in str(instance):
                start_instance_ids.append(instance['InstanceId'])
                name_tag_exists = False
                try:
                  if instance['Tags']:
                      for tag in instance['Tags']:
                        if tag['Key'] == 'Name' and tag['Value'] != '':
                          print tag['Value'], instance['InstanceId']
                          start_instances[tag['Value']] = instance['InstanceId']
                          name_tag_exists = True
                      if name_tag_exists == False:
                          print 'noname', instance['InstanceId']
                          start_instances['noname'].append(instance['InstanceId'])
                except:
                  pass
    print 'Starting Instances List:', start_instance_ids
    if start_instances['noname'] == []:
        start_instances.pop('noname')
    if start_instances:
        send_message('*' + region + ' EC2 Resources to be started at ' + str(current_time) +  '*', type='title')
        send_message(str(start_instances))
        send_message('_' +  str(args) + '_', type='title')
        send_message('\r')
    if apply and start_instance_ids:
        ec2.start_instances(InstanceIds=start_instance_ids)

def list_instances(region, filters):
    current_time = datetime.datetime.utcnow()
    start_instance_ids = []
    ec2 = boto3.client('ec2', region_name=region)
    ec2_instances = ec2.describe_instances(Filters=filters)
    print region, 'EC2 Resources state at',current_time
    for reservation in ec2_instances["Reservations"]:
        for instance in reservation["Instances"]:
            name_tag_exists = False
            try:
              if instance['Tags']:
                  for tag in instance['Tags']:
                    if tag['Key'] == 'Name':
                      print tag['Value'], instance['InstanceId'], instance['State']['Name'], instance['InstanceType']
                      name_tag_exists = True
                  if name_tag_exists == False:
                      print 'noname', instance['InstanceId'], instance['State']['Name'], instance['InstanceType']
            except:
              pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='ec2_janitor.py --region us-west-2  --tag-owner Training --apply --action stop')
    parser.add_argument("--region", required=True,
                        dest='region', default='ca-central-1')
    parser.add_argument("--tag-owner", required=False,
                        dest='tag_owner', help='Owner Tag Search mask: *tag_owner')
    parser.add_argument("--tag-key", required=False,
                        dest='tag_key', help='Custom Tag Search')
    parser.add_argument("--tag-value", required=False,
                        dest='tag_value', help='Custom Tag Search')
    parser.add_argument("--lab-timezone", required=False,
                            dest='lab_timezone', help='Supported lab timezones: EST, PST, GMT, SGT')
    parser.add_argument("--exclude-tag", required=False,
                        dest='exclude_tag', default='EXCLUDE_TAG', help='Exclude from action based on tag')
    parser.add_argument("--action", required=True,
                        dest='action', help='Supported actions: stop, start or list', default=None)
    parser.add_argument("--apply",  action='store_true',
                        dest='apply', help='Apply changes', default=None)
    args = parser.parse_args()

    if args.tag_owner:
        filters = [{
            'Name': 'tag:Owner',
            'Values': ['*'+args.tag_owner]
        }]
    elif args.tag_key and args.tag_value:
        filters = [{
            'Name': 'tag:'+args.tag_key,
            'Values': [args.tag_value]
        }]
    elif args.tag_key:
        filters = [{
            'Name': 'tag:'+args.tag_key,
            'Values': ['*']
        }]
    if args.lab_timezone:
        print "Lab Timezone:", args.lab_timezone
        filters.append({
            'Name': 'tag:Lab_Timezone',
            'Values': [args.lab_timezone]
        })
    if args.action == 'stop':
        stop_instances(region=args.region, filters=filters, exclude_tag=args.exclude_tag, apply=args.apply)
    elif args.action == 'start':
        start_instances(region=args.region, filters=filters, exclude_tag=args.exclude_tag, apply=args.apply)
    elif args.action == 'list':
        list_instances(region=args.region, filters=filters)
    print args
