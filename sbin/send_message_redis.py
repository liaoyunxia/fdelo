import datetime
import sys
from time import sleep
import time

import redis

from py_mysql import MysqlClient
from sms_ytx_sdk import sendTemplateSms


def redis_master(user_id=None):
    if not user_id:
        return 0
    else:
        if user_id < 10000:
            return 0
        else:
            return int(user_id / 1000)


def timestamp(date):
    return time.mktime(date.timetuple())


def generate_shard_id(user_id):
    time_offset = int(timestamp(datetime.datetime.now()) - 1425168000)  # 2015-03-01 00:00:00
    return user_id | time_offset << 32


if __name__ == '__main__':
    TEST_ENV = int(sys.argv[1])
    if TEST_ENV:
        redis_client = redis.Redis(host='121.41.8.31',
                                   port=6379,
                                   db=0)
    else:
        redis_client = redis.Redis(host='e6837b0ac94b4118.m.cnhza.kvstore.aliyuncs.com',
                                   port=6379,
                                   db=0,
                                   password='e6837b0ac94b4118:ReO119fh1c')
    while True:
        queryset = redis_client.rpop('message_queue_key')
        if queryset:
            queryset = eval(queryset)
            user_key = 'user_message:{}'.format(redis_master(queryset['user_id']))
            message_list = []
            if redis_client.hexists(user_key, 'data:{}'.format(queryset['user_id'])):
                    message_list = eval(redis_client.hget(user_key, 'data:{}'.format(queryset['user_id'])))
            message = queryset
            message['id_str'] = "{}".format(generate_shard_id(queryset['user_id']))
            message['template_id'] = "{}".format(queryset['type'])
            message_list.append(message)
            redis_client.hset(user_key, 'data:{}'.format(queryset['user_id']), message_list)
        else:
            sleep(1)
