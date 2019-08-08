from django.utils.safestring import mark_safe

from srt.deliveries.models import Delivery, History
from srt.core.models import STATUS
from srt.core.mixins import BaseAdminMixin


class TargetAdminMixin(BaseAdminMixin):

    def deliveries_url(self, obj):
        return self.get_url(Delivery, plural='deliveries', target=obj.id)
    deliveries_url.short_description = 'Deliveries'


class DeliveryAdminMixin(BaseAdminMixin):

    def report_url(self, obj):
        if obj.report:
            html = self.get_href(obj.report.change_url, obj.report.name)
            return mark_safe(html)
        return ''
    report_url.short_description = 'Report'

    def target_url(self, obj):
        if obj.target:
            html = self.get_href(obj.target.change_url, obj.target.name)
            return mark_safe(html)
        return ''
    target_url.short_description = 'Target'

    def delivered_url(self, obj):
        return self.get_url(History, singular='delivered', plural='delivered', delivery=obj.id)
    delivered_url.short_description = 'Delivered'


class HistoryAdminMixin(BaseAdminMixin):

    def history_url(self, obj):
        report_history = obj.history
        if not report_history:
            return None

        try:
            report_name = report_history.report.name
        except AttributeError:
            report_name = '&lt;deleted&gt;'

        label = '%s (history %s)' % (report_name, obj.history.id)
        return self.get_change_url(obj.history, label)
    history_url.short_description = 'Report'

    def delivery_url(self, obj):
        label = '%s (delivery %s)' % (obj.delivery.target.name, obj.delivery.id)
        return self.get_change_url(obj.delivery, label)
    delivery_url.short_description = 'Delivery'

    def msg_url(self, obj):
        if obj.status == STATUS.completed:
            link = obj.source
            html = self.get_href(link, obj.get_filename('source'), target='_blank')
            return mark_safe(html)
        return self.msg_short(obj)
    msg_url.short_description = 'Message'

    def file_url(self, obj):
        html = self.get_href(obj.url, obj.delivery.name, target='_blank') if obj.url else '-'
        return mark_safe(html)
    file_url.short_description = 'Report'
