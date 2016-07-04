"""
* 短信接口库:
*==============================
*[发送普通短信] --Mdsmssend:
"""
import hashlib
import os
import time
from urllib.parse import quote

import requests

from nyssance.utils.func_ext import formatBizQueryParaMap
import xml.etree.ElementTree as ET


class SendSMS_pub():
    """配置短信账号信息"""
    def __init__(self):
        self.BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.SP_KEY = 'DXX-BBX-11U-19553'
        self.SP_PASSWD = '893712'
        self.parameters = {}  #请求参数，类型为关联数组
        self.result = {}      #返回参数，类型为关联数组

    def trimString(self, value):
        if value is not None and len(value) == 0:
            value = None
        return value

    def set_parameter(self, parameter, parameterValue):
        """设置请求参数"""
        self.parameters[self.trimString(parameter)] = self.trimString(parameterValue)

    def Mdsmssend_pub(self):
        url = self.get_mdsms_params()
        self.response = requests.get(url).text
        result = self.getResult()
        if int(result) != int(self.url_dict['rrid']):
            return False
        return True

    def getResult(self):
        """获取结果，默认不使用证书"""
        self.result = self.xmlToArray(self.response)
        return self.result

    def xmlToArray(self, xml):
        root = ET.fromstring(xml)
        return root.text

    def get_mdsms_params(self):
        url_obj = self.parameters
        url_obj['sn'] = self.SP_KEY
        url_obj['pwd'] = self.get_pwd()
        url_obj['ext'] = ''
        url_obj['stime'] = ''
        url_obj['stime'] = ''
        url_obj['msgfmt'] = ''
        url_obj['rrid'] = int(time.time())
        self.url_dict = url_obj
        bizString = formatBizQueryParaMap(url_obj, False)
        return "http://sdk.entinfo.cn:8061/webservice.asmx/mdsmssend?" + bizString

    def get_pwd(self):
        String = '{}{}'.format(self.SP_KEY, self.SP_PASSWD)
        return hashlib.md5(String.encode()).hexdigest().upper()
