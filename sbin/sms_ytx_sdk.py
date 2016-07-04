from base64 import b64encode
import hashlib
import json
import time
import syslog

import requests


class sendTemplateSms():
    '''用来发送通知短信的应用'''
    def __init__(self):
        self.accountSid = 'aaf98f8951eb7f810151f189e5970ea3'
        self.accountToken = 'cc36e2edc9e9443ca5f2ff6f5191dc33'
        # self.appId = '8a48b551523a5c1201523e9e8f3b0a01'
        self.serverIP = 'https://app.cloopen.com'
        self.serverPort = '8883'
        self.softVersion = '2013-12-26'
        self.local_time = self.get_local_time()

    def send_template_sms(self, to, msg, template_id, app_name):
        if app_name == 'invest':
            app_id = '8a48b551523a5c1201523e9e8f3b0a01'
        else:
            app_id = 'aaf98f895350b688015354bb7bf8072d'
        url = '{}:{}{}'.format(self.serverIP, self.serverPort, self.get_request_header())
        headers = self.get_http_header()
        data = self.get_request_params(to, msg, template_id, app_id)
        result = requests.post(url=url, data=json.dumps(data), headers=headers).text
        print(result)
        self.write_log('send_sms_msg:{}'.format(to), '{}'.format(result))
        if 'statusCode' in result:
            statusCode = json.loads(result)['statusCode']
            if statusCode == '000000':
                return True
        return False

    def get_request_header(self):
        return '/{}/Accounts/{}/SMS/TemplateSMS?sig={}'.format(self.softVersion, self.accountSid, self.get_sig())

    def get_http_header(self):
        auth_str = '{}:{}'.format(self.accountSid, self.local_time)
        return {'Accept': 'application/json',
                'Content-Type': 'application/json;charset=utf-8',
                'Content-Length': 1024,
                'Authorization': b64encode(auth_str.encode()).decode()}

    def get_request_params(self, to, data=['', ''], template_id='1', app_id=''):
        request_params = {'to': to,
                          'appId': app_id,
                          'templateId': template_id,
                          'datas': data}
        return request_params

    def get_sig(self):
        '''账户Id + 账户授权令牌 + 时间戳'''
        sig_str = '{}{}{}'.format(self.accountSid, self.accountToken, self.local_time)
        return hashlib.md5(sig_str.encode()).hexdigest().upper()

    def get_local_time(self):
        return time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))

    def write_log(self, method, msg):
        syslog.openlog(method, syslog.LOG_LOCAL0)
        syslog.syslog(syslog.LOG_INFO, msg)
