import locale

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from import_export.admin import ExportMixin

from nyssance.django.db.models import OwnerModel


class ImageUrlsMixin(object):
    image_width = 200
    image_height = 100

    def get_preview(self, obj):
        html = '<br />'.join('<a href="{0}" rel="external" target="_blank"><img src="{0}" width="{1}" height="{2}"/></a>'.format(item.strip(), self.image_width, self.image_height) for item in obj.image_urls.split('\n'))
        return format_html(html)
    get_preview.short_description = _('preview')


class SuperAdmin(ImageUrlsMixin, ExportMixin, admin.ModelAdmin):
    # list_filter = ('is_active',)

    def save_model(self, request, obj, form, change):
        if not obj.id:  # 如果obj.id不存在, 为新创建.
            obj.user_id = request.user.id
            if isinstance(obj, OwnerModel):
                obj.username = request.user.username
                obj.user_image_urls = request.user.image_urls
        super(SuperAdmin, self).save_model(request, obj, form, change)

    def format_currency(self, amount, min):
        price = amount / 100
        locale.setlocale(locale.LC_ALL, '')
        formatted = locale.currency(price, symbol=False, grouping=True)
        if price < min:
            return '{}<span style="color: red;"> (低于{})</span>'.format(formatted, locale.currency(min, symbol=False, grouping=True))
        else:
            return formatted
