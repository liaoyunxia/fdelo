import hashlib
import json
import re
import time
import urllib

from django.conf import settings
import pylibmc

from nyssance.weixin.get_sign import Common_util_pub

from .get_sign import WxPayConf_pub, HttpClient
import syslog


def write_log(method, msg):
    syslog.openlog(method, syslog.LOG_LOCAL0)
    syslog.syslog(syslog.LOG_INFO, msg)


class WX_JSSDK():
    def __init__(self):
        self.mc = pylibmc.Client([settings.CACHES['default']['LOCATION']])
        self.api_ticket_key = '{}_api_ticket'.format(WxPayConf_pub().APPID)

    def get_config_params(self, url):
        # api_ticket = self.mc.get(self.api_ticket_key)
        # if not api_ticket:
            # api_ticket = self.get_api_ticket(self.get_access_token())
        api_ticket = self.get_jsapi_ticket_sync()
        config_params = {'timestamp': int(time.time()),
                         'nonceStr': Common_util_pub().createNoncestr(32),
                         'jsapi_ticket': api_ticket,
                         'url': '{}{}'.format(settings.BASE_URL, url)
                         }
        config_params = self.configSign(config_params)
        return config_params

    def get_weinxin_auth_url(self, url, additional=''):
        # 设置微信验证 获取open_id
        if url.find('?') >= 0:
            url_path = '{}{}'.format(settings.BASE_URL, url)
            if url_path.find('open_id=') >= 0:
                if re.search('open_id=.*&', url_path):
                    url_path = re.sub('open_id=.*&', '', url_path) if (url_path.find('?open_id=') >= 0) else re.sub('open_id=.*&', '&', url_path)
                else:
                    url_path = re.sub('open_id=.*', '', url_path)
            url_path += ('&open_id=' if url_path[-1] != '&' else 'open_id=')
        else:
            url_path = '{}{}{}'.format(settings.BASE_URL, url, '?open_id=')
        url_path += additional
        url_path = urllib.request.quote(urllib.request.quote(url_path))
        agent_domain = 'http://test.weixin.cmcaifu.com' if settings.TEST_ENV else 'https://weixin.cmcaifu.com'
        redirect_uri = '{}/xmcxprj/redirect_share_page.action?url={}'.format(agent_domain, url_path)
        real_url = 'https://open.weixin.qq.com/connect/oauth2/authorize?appid={}&redirect_uri={}&response_type=code&scope=snsapi_base&state=1#wechat_redirect'.format(WxPayConf_pub().APPID, redirect_uri)
        return real_url

    def get_wx_share_params(self, title, desc, url, image_url):
        share_params = {'title': title,
                        'desc': desc,
                        'link': "{}{}".format(settings.BASE_URL, url),
                        'imgUrl': image_url}
        return dict(filter(lambda x: x[1] != '', share_params.items()))

    def get_access_token(self):
        url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}'.format(WxPayConf_pub().APPID, WxPayConf_pub().APPSECRET)
        result = HttpClient().get(url)
        result_data = json.loads(result.decode('gb2312'))
        key = '{}_api_token'.format(WxPayConf_pub().APPID)
        self.mc.set(key, result_data['access_token'], result_data['expires_in'])
        return json.loads(result.decode('gb2312'))['access_token']

    def get_access_token_sync(self):
        agent_domain = 'weixin.czyx.cc:81' if settings.TEST_ENV else '182.92.24.162:8088'
        url = 'http://{}/xmcxapi/webService/systemoption/getWeixinAccessToken'.format(agent_domain)
        result = HttpClient().get(url)
        # print('access_token---------{}'.format(result.decode()))
        write_log('get_access_token_sync', 'first 10 words of weixin access key:{}, domain:{}'.format(result.decode()[:10], agent_domain))
        return result.decode()

    def get_api_ticket(self, access_token):
        url = 'https://api.weixin.qq.com/cgi-bin/ticket/getticket?access_token={}&type=jsapi'.format(access_token)
        result = HttpClient().get(url)
        result_data = json.loads(result.decode('gb2312'))
        key = '{}_api_ticket'.format(WxPayConf_pub().APPID)
        self.mc.set(key, result_data['ticket'], result_data['expires_in'])
        return result_data['ticket']

    def get_jsapi_ticket_sync(self):
        agent_domain = 'weixin.czyx.cc:81' if settings.TEST_ENV else '182.92.24.162:8088'
        url = 'http://{}/xmcxapi/webService/systemoption/getWeixinJsApiTicket'.format(agent_domain)
        result = HttpClient().get(url)
        # print('jsapi_ticket---------{}'.format(result.decode()))
        write_log('get_jsapi_ticket_sync', 'first 10 words of weixin jsapi ticket:{}, domain:{}'.format(result.decode()[:10], agent_domain))
        return result.decode()

    def get_api_ticket_sync(self):
        agent_domain = 'weixin.czyx.cc:81' if settings.TEST_ENV else '182.92.24.162:8088'
        url = 'http://{}/xmcxapi/webService/systemoption/getWeixinApiTicket'.format(agent_domain)
        result = HttpClient().get(url)
        # print('api_ticket---------{}'.format(result.decode()))
        write_log('get_api_ticket_sync', 'first 10 words of weixin api ticket:{}, domain:{}'.format(result.decode()[:10], agent_domain))
        return result.decode()

    def configSign(self, ret):
        string = '&'.join(['%s=%s' % (key.lower(), ret[key]) for key in sorted(ret)])
        ret['signature'] = hashlib.sha1(string.encode()).hexdigest()
        ret['appid'] = WxPayConf_pub().APPID
        del ret['jsapi_ticket']
        return ret
