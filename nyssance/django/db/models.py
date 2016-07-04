from django.db import models
from datetime import date
from django.utils.translation import ugettext_lazy as _
from .utils import generate_shard_id, get_user_id, db_master
GENDER_CHOICES = (('m', _('男')), ('f', _('女')))
BIR_CHOICES = {"浙江": ["杭州", "宁波"], "湖北": ["武汉", "黄石", '荆门']}

LOCATION_CHOICE = (('beijing', _('北京')), ('shanghai', _('上海')),
                   ('guangzhou', _('广州')), ('shenzhen', _('深圳')),
                   ('hangzhou', _('杭州')), ('suzhou', _('苏州')),
                   ('HongKong', _('香港')), ('America', _('美国')),
                   ('Europe', _('欧洲')), ('others', _('其他')),)

STAR_SIGN_CHOICE = (('0', _('白羊座')), ('1', _('金牛座')),
                    ('2', _('双子座')), ('3', _('巨蟹座')),
                    ('4', _('狮子座')), ('5', _('处女座')),
                    ('6', _('天秤座')), ('7', _('天蝎座')),
                    ('8', _('射手座')), ('9', _('摩羯座')),
                    ('10', _('水瓶座')), ('11', _('双鱼座')),)


class DateTimeModelMixin(models.Model):
    created_time = models.DateTimeField(_('created_time'), auto_now_add=True)
    updated_time = models.DateTimeField(_('updated_time'), auto_now=True)

    class Meta:
        abstract = True


class PersonalInfoMixin(DateTimeModelMixin):
    username = models.CharField(_('username'), max_length=200, blank=True)
    english_name = models.CharField(_('english_name'), max_length=100, blank=True)
    user_image_urls = models.CharField(_('user_image_urls'), max_length=2000, blank=True)
    gender = models.CharField(_('gender'), choices=GENDER_CHOICES, max_length=10, blank=True)
    email = models.EmailField(_('email'), blank=True)
    phone_number = models.CharField(_('phone_number'), max_length=20, blank=True)

    birthplace = models.CharField(_('birthplace'), max_length=200, blank=True)
    birth_year = models.DateField(_('birth_year'), default=date(2016, 1, 1), blank=True)
    star_sign = models.CharField(_('star_sign'), max_length=10, choices=STAR_SIGN_CHOICE, default='1')
    university = models.CharField(_('university'), max_length=100, blank=True)
    location = models.CharField(_('location'), max_length=200, default='shanghai', choices=LOCATION_CHOICE)
    roadshow_style = models.CharField(_('roadshow_style'), max_length=200, blank=True)

    about = models.CharField(_('about'), max_length=200, blank=True)
    tags = models.CharField(_('tags'), max_length=200, blank=True)
    remarks = models.CharField(_('remarks'), max_length=200, blank=True)

    class Meta:
        abstract = True


class OwnerModel(DateTimeModelMixin):
    user_id = models.IntegerField(default=0, editable=False)
    username = models.CharField(max_length=30, editable=False)
    user_image_urls = models.CharField(_('image_urls'), max_length=2000, blank=True, editable=False)
    is_active = models.BooleanField(_('active'), default=True)
    nickname = models.CharField(max_length=30, blank=True, editable=False)

    class Meta:
        abstract = True
        ordering = ['-pk']


class PostModel(OwnerModel):
    """内容发布类模型"""
    title = models.CharField(_('title'), max_length=30)
    summary = models.CharField(_('summary'), max_length=200, blank=True)
    image_urls = models.CharField(_('image_urls'), max_length=2000, blank=True)
    tags = models.CharField(_('tags'), max_length=200, blank=True)

    class Meta(OwnerModel.Meta):
        abstract = True

    def __str__(self):
        return self.title


class ShardModel(OwnerModel):
    id = models.BigIntegerField(primary_key=True, editable=False)

    class Meta(OwnerModel.Meta):
        abstract = True

    def save(self, using='default', *args, **kwargs):
        self.full_clean()
        if self.pk is None:
            self.pk = generate_shard_id(self.user_id)
        super(ShardModel, self).save(using=db_master(self.user_id), *args, **kwargs)


class ShardLCModel(OwnerModel):
    id = models.BigIntegerField(primary_key=True, editable=False)
    is_origin = models.BooleanField(default=True)

    class Meta(OwnerModel.Meta):
        abstract = True

    def save(self, using='default', *args, **kwargs):
        self.full_clean()
        if self.pk is None:  # Create
            self.pk = generate_shard_id(self.user_id)
            self.is_origin = True
        super(ShardLCModel, self).save(using=db_master(self.user_id), *args, **kwargs)  # 保存第一份.
        card_user_id = get_user_id(self.card_id)
        if db_master(card_user_id) != db_master(self.user_id):  # 保存第二份.
            self.is_origin = False
            super(ShardLCModel, self).save(using=db_master(card_user_id), *args, **kwargs)
