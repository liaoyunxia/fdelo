"""
* 短信接口库:
*==============================
*[发送普通短信] --Mdsmssend:
"""
import hashlib
import os
from urllib.parse import quote

import requests

from nyssance.utils.func_ext import formatBizQueryParaMap
import xml.etree.ElementTree as ET


class SendZwSms():
    """配置短信账号信息"""
    def __init__(self):
        self.BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.userId = '412'
        self.account = 'fuhuazhongjinhy6'
        self.password = '8hhX6gpsx'
        self.parameters = {}  #请求参数，类型为关联数组
        self.result = {}      #返回参数，类型为关联数组
        self.url = 'http://hy6.nbark.com:7602/sms.aspx'

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
        print(result)
        if result.get('returnstatus') == 'Success':
            return True
        return False

    def getResult(self):
        """获取结果，默认不使用证书"""
        self.result = self.xmlToArray(self.response)
        return self.result

    def xmlToArray(self, xml):
        """将xml转为array"""
        array_data = {}
        root = ET.fromstring(xml)
        for child in root:
            value = child.text
            array_data[child.tag] = value
        return array_data

    def get_mdsms_params(self):
        url_obj = self.parameters
        url_obj['userid'] = self.userId
        url_obj['account'] = self.account
        url_obj['password'] = self.password
        url_obj['sendTime'] = ''
        url_obj['action'] = 'send'
        url_obj['extno'] = ''
        self.url_dict = url_obj
        bizString = formatBizQueryParaMap(url_obj, False)
        return "{}?".format(self.url) + bizString

    def formatBizQueryParaMap(self, paraMap, urlencode):
        """格式化参数，签名过程需要使用"""
        slist = sorted(paraMap)
        buff = []
        for k in slist:
            v = quote(paraMap[k]) if urlencode else paraMap[k]
            buff.append("{0}={1}".format(k, v))

        return "&".join(buff)

    def get_pwd(self):
        String = '{}{}'.format(self.SP_KEY, self.SP_PASSWD)
        return hashlib.md5(String.encode()).hexdigest().upper()
