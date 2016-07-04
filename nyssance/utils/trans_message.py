from nyssance.django.db.utils import unixtime_to_datetime


class TransMessage():
    def __init__(self, data, app_name):
        self.data = data
        self.app_name = app_name

    def trans_message(self):
        template_id = int(self.data.get('template_id'))
        if template_id == 1:
            return self.get_payment_succ()
        elif template_id == 3:
            return self.get_withdraw_succ()
        elif template_id == 4:
            return self.get_withdraw_fail()
        elif template_id == 5:
            return self.get_kaihu_succ()
        elif template_id == 6:
            return self.get_bind_succ()
        elif template_id == 7:
            return self.get_dongjie_message()
        elif template_id == 8:
            return self.get_full_bill_message()
        elif template_id == 9:
            return self.get_bill_fail_message()
        elif template_id == 10:
            return self.get_repayment_succ()
        elif template_id == 11:
            return self.get_cm_refund()  # 超募退款.
        elif template_id == 12:
            return self.get_register_code()
        elif template_id == 13:
            return self.get_vip_code()
        elif template_id == 14:
            return self.get_zst_code()
        elif template_id == 15:
            return self.get_xz_register_code()  # 血族注册.
        elif template_id == 16:
            return self.get_xz_tz_code()  # 血族渠道投资返现.
        elif template_id == 17:
            return self.get_not_xz_tz_code()  # 非血族渠道投资返现.

    def get_payment_succ(self):
        title = '充值成功通知'
        url = self.get_url('transactions')
        content = '您于{}发起的{}元人民币的充值业务已受理成功，当前账户余额:{}元。 '.format(self.data.get('date'), self.data.get('amount', 0) / 100, self.data.get('balance', 0) / 100)
        return self.get_message_dict(title, content, url)

    def get_withdraw_succ(self):
        title = '提现成功通知'
        url = self.get_url('transactions')
        content = '您于{}申请的{}元人民币的提现业务已受理成功，资金到账时间为受理成功日（不含当日）起两个工作日内，请注意查收。'.format(self.data.get('date'), self.data.get('amount', 0) / 100)
        return self.get_message_dict(title, content, url)

    def get_withdraw_fail(self):
        title = '提现失败通知'
        content = '您于{}申请的{}元人民币的提现业务已受理失败。'.format(self.data.get('date'), self.data.get('amount', 0) / 100)
        return self.get_message_dict(title, content)

    def get_kaihu_succ(self):
        title = '中金开户成功通知'
        content = '您于{}在中金支付成功开户'.format(self.data.get('date'))
        return self.get_message_dict(title, content)

    def get_bind_succ(self):
        title = '中金绑卡成功通知'
        content = '您于{}在中金支付绑卡成功'.format(self.data.get('date'))
        return self.get_message_dict(title, content)

    def get_dongjie_message(self):
        title = '投标冻结资金通知'
        url = self.get_url('investments')
        content = '您向“{}”产品投资的 {}元资金已被冻结。产品募集成功后将自动划转至融资方账户并开始计息'.format(self.data.get('product_name'), self.data.get('amount', 0) / 100)
        return self.get_message_dict(title, content, url)

    def get_full_bill_message(self):
        title = '投资满标通知'
        url = self.get_url('investments')
        content = '您投资{}元的“{}”产品已成功满标，将于{}开始计息。'.format(self.data.get('amount', 0) / 100, self.data.get('product_name'), self.data.get('date', ''))
        return self.get_message_dict(title, content, url)

    def get_bill_fail_message(self):
        title = '投资流标通知'
        url = self.get_url('investments')
        content = '我们非常抱歉的通知您，您投资的“{}”产品由于募集金额不足已流标，您投资的 {}元款项已返还至您的账户。 我们对由此造成的不便深表歉意。'.format(self.data.get('product_name'), self.data.get('amount', 0) / 100)
        return self.get_message_dict(title, content, url)

    def get_repayment_succ(self):
        title = '投资还款通知'
        url = self.get_url('investments')
        content = '您所投资“{}”产品的还款{}已转入您的账户，请注意查收。'.format(self.data.get('product_name'), self.data.get('amount', 0) / 100)
        return self.get_message_dict(title, content, url)

    def get_cm_refund(self):
        title = '超募退款通知'
        content = '您向{}产品投资的{}元资金，由于多人同时投资导致了超募的情况，您的认购资金中{}元已投资生效，剩余{}元已自动退款至您的账户余额中。'.format(self.data.get('product_name'), self.data.get('amount', 0) / 100, self.data.get('real_deal_amount') / 100, self.data.get('refund_amount') / 100)
        return self.get_message_dict(title, content, '')

    def get_register_code(self):
        title = '兑换码领取通知'
        content = '您已成功获取法宝网"注册邀请码"一枚：{},请及时去法宝网注册 www.ifabao.com.'.format(self.data.get('code', ''))
        return self.get_message_dict(title, content, '')

    def get_vip_code(self):
        title = '兑换码领取通知'
        content = '您已成功获取法宝网"VIP抵价券"一枚：{}，请及时去论坛内领奖兑换。'.format(self.data.get('code', ''))
        return self.get_message_dict(title, content, '')

    def get_zst_code(self):
        title = '兑换码领取通知'
        content = '您已成功获取{}"兑换码"一枚：{}。'.format(self.data.get('product_name', ''), self.data.get('code', ''))
        return self.get_message_dict(title, content, '')

    def get_xz_register_code(self):
        title = '血族注册开户返现通知'
        content = '您已成功开户并获得返现{}元。还有一大波返现活动正在进行，快来投资吧!'.format(self.data.get('amount', 0) / 100)
        url = self.get_url('/activities/online/', True)
        return self.get_message_dict(title, content, url)

    def get_xz_tz_code(self):
        title = '投资返现通知'
        content = '您已累计投资满{}元，获得奖励返现{}元。'.format(self.data.get('total_amount', 0) / 100, self.data.get('amount', 0) / 100)
        url = self.get_url('/activities/online/', True)
        return self.get_message_dict(title, content, url)

    def get_not_xz_tz_code(self):
        title = '投资返现通知'
        content = '您已成功获取"{}"，兑换码为：{}。'.format(self.data.get('product_name', ''), self.data.get('code'))
        return self.get_message_dict(title, content, '')

    def get_message_dict(self, title, content, url=''):
        created_time = self.data.get('handled_time', 0)
        if created_time != 0:
            created_time -= 8 * 60 * 60
        notify_data = {'title': title,
                       'content': content,
                       'id_str': self.data.get('id_str', 0),
                       'id': int(self.data.get('id_str', 0)),
                       'url': url,
                       'created_time': unixtime_to_datetime(created_time)}
        return notify_data

    def get_url(self, url, full=False):
        if self.app_name == 'mm':
            return 'mm://{}'.format(url)
        else:
            if not full:
                return '/accounts/{}'.format(url)
            else:
                return url
