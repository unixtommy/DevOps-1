# -*- coding:utf-8 -*-
# !/usr/bin/env python
# Time 18-7-2
# Author WZZ
# import os
# import django
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "deveops.settings")
# django.setup()

import json
from django.conf import settings
from aliyunsdkcore import client
from aliyunsdkrds.request.v20140815 import DescribeDBInstancesRequest
import datetime


class AliyunRDSTool(object):
    def __init__(self):
        self.clt = client.AcsClient(settings.ALIYUN_ACCESSKEY, settings.ALIYUN_ACCESSSECRET, 'cn-hangzhou')
        self.pagecount = self.get_page_number()

    @staticmethod
    def get_json_results(results):
        return json.loads(results.decode('utf-8'))

    @staticmethod
    def is_readonly(results):
        if results.get('DBInstanceId')[0:2] == 'rr' or results.get('DBInstanceId')[0:2]:
            return True
        else:
            return False

    @staticmethod
    def request_to_json(request):
        return request.set_accept_format('json')

    def get_page_number(self):
        request = DescribeDBInstancesRequest.DescribeDBInstancesRequest()
        request.add_query_param('PageNumber', 1)
        request.add_query_param('PageSize', 1)
        try:
            response = self.clt.do_action_with_exception(request)
        except:
            return {}
        result = self.get_json_results(response)
        return int(result.get('TotalRecordCount')/settings.ALIYUN_PAGESIZE)+1

    def get_instance(self, instance_id):
        request = DescribeDBInstancesRequest.DescribeDBInstancesRequest()
        self.request_to_json(request)
        request.add_query_param('RegionId', 'cn-hangzhou')
        request.add_query_param('DBInstanceId', instance_id)
        try:
            response = self.clt.do_action_with_exception(request)
        except:
            return {}
        return self.get_json_results(response).get('Items').get('DBInstance')[0]

    def get_instances(self, page):
        request = DescribeDBInstancesRequest.DescribeDBInstancesRequest()
        self.request_to_json(request)
        request.add_query_param('RegionId', 'cn-hangzhou')
        request.add_query_param('PageNumber', page)
        request.add_query_param('PageSize', settings.ALIYUN_PAGESIZE)
        try:
            response = self.clt.do_action_with_exception(request)
        except:
            return {}
        return self.get_json_results(response).get('Items').get('DBInstance')

    @staticmethod
    def get_expired_day(time):
        expired = datetime.datetime.strptime(time, '%Y-%m-%dT%H:%M:%SZ')
        return (expired-datetime.datetime.now()).days

    @staticmethod
    def get_aliyun_expired_models(json_results):
        return {
            'expired': AliyunRDSTool.get_expired_day(json_results.get('ExpireTime')),
            'recognition_id': json_results.get('DBInstanceId'),
            'instancename': json_results.get('DBInstanceDescription'),
            'version': json_results.get('EngineVersion'),
            'readonly': len(json_results['ReadOnlyDBInstanceIds']['ReadOnlyDBInstanceId'])
        }

    # @staticmethod
    # def get_aliyun_models(json_results):
    #     return {
    #         'aliyun_id': json_results.get('DBInstanceId'),
    #         'name': json_results.get('DBInstanceDescription')
    #     }