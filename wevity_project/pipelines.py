# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface

import json
import boto3

class S3Pipeline(object):
    def __init__(self):
        self.s3_client = boto3.client('s3')
        self.bucket_name = 'jh-capstone2-bucket'  # S3 버킷 이름을 설정하세요.

    def process_item(self, item, spider):
        # Convert item to JSON
        item_json = json.dumps(dict(item))
        # Generate a unique file name
        # file_name = f"list/contest_{item['title']}.json"
        file_name = f"list/contest_{item['title'][0].replace('/', '_')}.json"
        # Upload to S3
        self.s3_client.put_object(Bucket=self.bucket_name, Key=file_name, Body=item_json)
        return item
