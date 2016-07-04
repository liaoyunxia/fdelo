from collections import OrderedDict
import json
import time

from django.conf import settings
import requests

from nyssance.django.db.utils import datetime_to_unixtime
from nyssance.utils.func_ext import write_log


def get_status_images(code):
    data = [{'url': 'https:{}resources/status/product_{}.png'.format(settings.STATIC_URL, code)}]
    return OrderedDict([('count', len(data)), ('next', None), ('previous', None), ('results', data)])


def get_status_message(bill_status, obj):
    data = {'code': 0, 'message': '未知'}
    if bill_status == -200:
        data = {'code': -20, 'message': '项目关闭'}
    if bill_status in [0, -10, 50, 100]:
        data = {'code': 1, 'message': '未开标'}
    if obj.inventory > 0:
        if not obj.is_reservable and datetime_to_unixtime(obj.list_time) < int(time.time()) < datetime_to_unixtime(obj.open_time) and bill_status == 200:
            data = {'code': 5, 'message': '待开售'}
        elif obj.is_reservable and datetime_to_unixtime(obj.list_time) < int(time.time()) < datetime_to_unixtime(obj.open_time) and bill_status == 200:
            data = {'code': 8, 'message': '预约中'}
        elif datetime_to_unixtime(obj.open_time) < int(time.time()) < datetime_to_unixtime(obj.close_time) and bill_status == 200:
            data = {'code': 9, 'message': '抢购中'}
    if obj.inventory == 0 and datetime_to_unixtime(obj.open_time) < int(time.time()) < datetime_to_unixtime(obj.close_time) and bill_status == 200:
            data = {'code': 10, 'message': '满标'}
    if bill_status in [350, 375]:
        data = {'code': 15, 'message': '满 标'}
    if int(time.time()) > datetime_to_unixtime(obj.close_time) and bill_status == 200:
        data = {'code': 20, 'message': '认购结束'}
    if bill_status in [-20, -30, -40]:
        data = {'code': 30, 'message': '流标'}
    if bill_status in [375, 400, 450, 500]:
        data = {'code': 40, 'message': '计息中'}
    if bill_status in [550, 580]:
        data = {'code': 50, 'message': '还款中'}
    if bill_status == -150:
        data = {'code': 55, 'message': '还款逾期'}
    if bill_status == 600:
        data = {'code': 60, 'message': '已还款'}
    data['images'] = get_status_images(data['code'])
    return data


def get_progress_data(status, obj):
    if status['code'] == -20:
        return -200
    if status['code'] == 1:
        return -100
    if status['code'] == 5:
        return -50
    if status['code'] in [10, 15]:
        return 1
    if status['code'] == 20:
        return -2
    if status['code'] == 30:
        return -3
    if status['code'] == 40:
        return -4
    if status['code'] == 50:
        return -5
    if status['code'] == 55:
        return -5.5
    if status['code'] == 60:
        return -6
    if status['code'] == 70:
        return -7
    else:
        try:
            url = '{}/projects/invest_bill_fund_query'.format(settings.JAVA_API)
            headers = {'Content-Type': 'application/json'}
            write_log('bill_fund_query_url', '{}'.format(url))
            results = requests.post(url, data=json.dumps({'bill_id': obj.bill_id}), headers=headers).text
            write_log('bill_fund_query_result', '{}'.format(results))
            if 'ordered_total_price' in results:
                result = json.loads(results)
                return float('%.2f' % (result['ordered_total_price'] / obj.bill_max_fund))
        except:
            return 0
    return 0