# coding: utf-8

import utils
from snapshot import Snapshot

class Volume(object):
    ''' Represent Volume class '''

    _config = {
        'target_tag': 'ebsant',
    }

    def __init__(self, ec2, raw):
        ''' Instance constructor

        Agrs:
            obj: self
            obj: ec2 object
            obj: volume raw object (which was returned from boto3 api)

        Returns: void

        '''
        self._ec2 = ec2
        self._raw = raw
        self._tags = None

    def get_config(self, key):
        return self._config.get('target_tag', None)

    def get_id(self):
        return self._raw.id

    def get_tags(self):
        if self._tags is None:
            tags = {}
            for t in self._raw.tags:
                tags.setdefault(t['Key'], t['Value'])
            self._tags = tags
        return self._tags

    def get_name(self):
        tags = self.get_tags()
        name = tags.get('Name', '')
        return name.strip()

    def get_snapshot_description(self):
        description = ' - '.join(['ebsant', self.get_id()])
        if self.get_name():
            description += ' (%s)' % self.get_name()
        return description

    def get_keep_days(self):
        tags = self.get_tags()
        keep_days = tags.get(self._config['target_tag'])
        if not utils.is_int(keep_days):
            keep_days = 0
        return int(keep_days)

    def get_snapshots(self):
        ec2 = self._ec2.get_resource()
        snapshots = ec2.snapshots.filter(
            Filters=[
                {
                    'Name': 'tag:'+self.get_config('target_tag'),
                    'Values': [self.get_id()]
                }
            ]
        )
        return [Snapshot(self, s) for s in snapshots]

    def create_snapshot(self):
        description = self.get_snapshot_description()
        snapshot = self._raw.create_snapshot(
            Description=description,
            TagSpecifications=[
                {
                    'ResourceType': 'snapshot',
                    'Tags': [
                        {'Key': 'Name', 'Value': self.get_name()},
                        {'Key': self.get_config('target_tag'), 'Value': self.get_id()}
                    ]
                },
            ]
        )
        return Snapshot(self, snapshot)
