from collections import OrderedDict
import datetime
import random
import time
from urllib.parse import quote

from django.conf import settings

import syslog


def write_log(method, msg):
    syslog.openlog(method, syslog.LOG_LOCAL0)
    syslog.syslog(syslog.LOG_INFO, msg)


class get_expired_time():
    def __init__(self):
        if settings.TEST_ENV:
            self.expired_time = 5 * 60
            self.offer_expired_time = 30 * 60
        else:
            self.expired_time = 2 * 60 * 60
            self.offer_expired_time = 24 * 60 * 60

    def get_enquiry_expired(self):
        return datetime.datetime.strptime(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() - self.expired_time)), '%Y-%m-%d %H:%M:%S')


def createNoncestr(chars, length=4):
    """产生随机字符串, 不长于32位"""
    strs = []
    for x in range(length):
        strs.append(chars[random.randrange(0, len(chars))])
    return ''.join(strs)


def formatBizQueryParaMap(paraMap, urlencode):
    """格式化参数，签名过程需要使用"""
    slist = sorted(paraMap)
    buff = []
    for k in slist:
        if k != 'sign':
            v = quote(paraMap[k]) if urlencode else paraMap[k]
            buff.append("{0}={1}".format(k, v))
    return "&".join(buff)


def trans_params(request):
    temp_dic = {}
    if request.user.is_authenticated():   # 判断用户是否登录.
        temp_dic['payment_account_number'] = request.user.payment_account_number
        temp_dic['user_id'] = request.user.id
        temp_dic['name'] = request.user.name
        temp_dic['phone_number'] = request.user.phone_number
        temp_dic['username'] = request.user.username
    for k, v in request.data.items():
        if k:
            temp_dic[k] = v
    return temp_dic


def get_result(count, data):
    return OrderedDict([('count', count), ('next', None), ('previous', None), ('results', data)])
