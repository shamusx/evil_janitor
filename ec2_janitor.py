#!/usr/bin/python
import argparse
import boto3
import datetime
import json
import requests

class Slack(object):
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url
    def send_message(self,message,type='text'):
        if type == 'title':
            slack_message = {"text": message }
        else:
            slack_message = {"attachments": [{"text":message }]}
        r = requests.post(self.webhook_url, data=json.dumps(slack_message), headers={'Content-Type': 'application/json'})
        if r.status_code != 200:
            raise ValueError('Request to slack returned an error %s, the response is:\n%s' % (r.status_code, r.text))

class Evil_Janitor(object):
    def __init__(self, region, filters, exclude_tag, webhook_url, apply=False, send_message=False, custom_message_header=None):
        self.region = region
        self.filters = filters
        self.exclude_tag = exclude_tag
        self.apply = apply
        self.send_message = send_message
        self.current_time = str(datetime.datetime.utcnow())
        self.ec2 = boto3.client('ec2',region_name=self.region)
        self.ec2_instances = self.ec2.describe_instances(Filters=self.filters)
        self.webhook_url = webhook_url
        self.slack = Slack(self.webhook_url)
        self.custom_message_header = custom_message_header


    def stop_instances(self):
        stop_instance_ids = []
        stop_instances = {}
        stop_instances['noname'] = []
        print self.region, 'EC2 resources to be stopped at', self.current_time
        for reservation in self.ec2_instances["Reservations"]:
            for instance in reservation["Instances"]:
                if instance['State']['Name'] == 'running' and self.exclude_tag not in str(instance):
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
                      print 'noname', instance['InstanceId']
                      stop_instances['noname'].append(instance['InstanceId'])
        print 'Stopping Instances List: ', stop_instance_ids
        if stop_instances['noname'] == []:
            stop_instances.pop('noname')
        if stop_instances and self.send_message:
            if self.custom_message_header:
                self.slack.send_message('*' + self.custom_message_header + '*',type='title')
            self.slack.send_message('*' + self.region + ' EC2 resources to be stopped at ' + self.current_time +  '*', type='title')
            self.slack.send_message(str(stop_instances))
            self.slack.send_message('_' +  str(args) + '_', type='title')
            self.slack.send_message('\r')
        if self.apply and stop_instance_ids:
            self.ec2.stop_instances(InstanceIds=stop_instance_ids)

    def start_instances(self):
        start_instance_ids = []
        start_instances = {}
        start_instances['noname'] = []
        print self.region, 'EC2 Resources to be started at', self.current_time
        for reservation in self.ec2_instances["Reservations"]:
            for instance in reservation["Instances"]:
                if instance['State']['Name'] == 'stopped' and self.exclude_tag not in str(instance):
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
                      print 'noname', instance['InstanceId']
                      start_instances['noname'].append(instance['InstanceId'])
        print 'Starting Instances List:', start_instance_ids
        if start_instances['noname'] == []:
            start_instances.pop('noname')
        if start_instances and self.send_message:
            if self.custom_message_header:
                self.slack.send_message('*' + self.custom_message_header + '*',type='title')
            self.slack.send_message('*' + self.region + ' EC2 Resources to be started at ' + self.current_time +  '*', type='title')
            self.slack.send_message(str(start_instances))
            self.slack.send_message('_' +  str(args) + '_', type='title')
            self.slack.send_message('\r')
        if self.apply and start_instance_ids:
            self.ec2.start_instances(InstanceIds=start_instance_ids)

    def list_instances(self):
        list_instance_ids = []
        list_instances = {}
        list_instances['noname'] = []
        print self.region, 'EC2 Resources state at', self.current_time
        for reservation in self.ec2_instances["Reservations"]:
            for instance in reservation["Instances"]:
                name_tag_exists = False
                if self.exclude_tag not in str(instance):
                  try:
                      for tag in instance['Tags']:
                        if tag['Key'] == 'Name' and tag['Value'] != '':
                            print tag['Value'], instance['InstanceId'], instance['State']['Name'], instance['InstanceType']
                            list_instances[tag['Value']] = instance['InstanceId']
                            name_tag_exists = True
                      if name_tag_exists == False:
                          print 'noname', instance['InstanceId'], instance['InstanceType']
                          list_instances['noname'].append(instance['InstanceId'])
                  except:
                    print 'noname', instance['InstanceId'], instance['InstanceType']
                    list_instances['noname'].append(instance['InstanceId'])
        if list_instances['noname'] == []:
            list_instances.pop('noname')
        if list_instances and self.send_message:
            if self.custom_message_header:
                self.slack.send_message('*' + self.custom_message_header + '*',type='title')
            self.slack.send_message('*' + self.region + ' EC2 Resources state at ' + self.current_time +  '*', type='title')
            self.slack.send_message(str(list_instances))
            self.slack.send_message('_' +  str(args) + '_', type='title')
            self.slack.send_message('\r')

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
                        dest='apply', help='Apply changes', default=False)
    parser.add_argument("--send-message",  action='store_true',
                        dest='send_message', help='Send slack message', default=False)
    parser.add_argument("--custom-message-header",  action='store',
                        dest='custom_message_header', help='Custom slack message header', default=None)
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
    else:
        filters = [{}]

    if args.lab_timezone:
        print "Lab Timezone:", args.lab_timezone
        filters.append({
            'Name': 'tag:Lab_Timezone',
            'Values': [args.lab_timezone]
        })


    webhook_url = ''
    evil_janitor = Evil_Janitor(region=args.region, filters=filters, exclude_tag=args.exclude_tag, webhook_url=webhook_url, apply=args.apply, send_message=args.send_message, custom_message_header=args.custom_message_header)

    if args.action == 'stop':
        evil_janitor.stop_instances()
    elif args.action == 'start':
        evil_janitor.start_instances()
    elif args.action == 'list':
        evil_janitor.list_instances()
    print args
