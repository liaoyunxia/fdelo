import sys
from time import sleep

import redis

from py_mysql import MysqlClient
from sms_ytx_sdk import sendTemplateSms
import syslog


def write_log(method, msg):
    syslog.openlog(method, syslog.LOG_LOCAL0)
    syslog.syslog(syslog.LOG_INFO, msg)


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
    send_template_sms = sendTemplateSms()
    while True:
        queryset = redis_client.rpop('sms_queue_key')
        if queryset:
            write_log('send_sms_message', '{}'.format(queryset))
            result = eval(queryset)
            params = {'name': ['phone_number'],
                      'tbl': 'accounts_user',
                      'prefix': 'where id={}'.format(result.get('user_id'))
                      }
            type_dict = {1: '63766',  # 起息.
                         2: '62023',  # 流标.
                         3: '62111',
                         4: '71074',
                         5: '71628',
                         6: '72035',
                         7: '73259',
                         8: '75835'}
            try:
                mysql_client = MysqlClient(TEST_ENV)
                mysql_client.selectQuery(params)
                query = mysql_client.getSql()
                app_name = 'invest'
                data = [result.get('product_name', ''), result.get('amount', 0) / 100]
                if result.get('type') == 1:
                    data = [result.get('amount', 0) / 100, result.get('product_name', ''), result.get('date', '')]
                if result.get('type') == 4:
                    data = [result.get('product_name', ''), result.get('amount', 0) / 100, result.get('real_deal_amount', 0) / 100, result.get('refund_amount', 0) / 100]
                if result.get('type') in [5, 6, 7, 8]:
                    data = [result.get('code', '')]
                    if result.get('type') in [7, 8]:
                        data = [result.get('product_name', ''), result.get('code', '')]
                    app_name = 'fabao'
                for item in query:
                    res = send_template_sms.send_template_sms(item.get('phone_number'), data, type_dict.get(result.get('type', 1)), app_name)
                mysql_client.close()
            except Exception as e:
                write_log('send_sms_error', '{}'.format(e))
        else:
            sleep(1)
