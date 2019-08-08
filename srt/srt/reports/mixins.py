from django.utils.safestring import mark_safe

from srt.core.mixins import BaseAdminMixin


class ReportAdminMixin(BaseAdminMixin):

    def histories_url(self, obj):
        from srt.reports.models import History
        return self.get_url(History, singular='history', plural='histories', report=obj.id)
    histories_url.short_description = 'Histories'


class HistoryAdminMixin(BaseAdminMixin):

    def path_url(self, obj):
        return mark_safe(self.get_href(obj.path, "Download", target='_blank'))
    path_url.short_description = 'Path'
