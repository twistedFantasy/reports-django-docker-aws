from srt.core.mixins import BaseAdminMixin


class ReportAdminMixin(BaseAdminMixin):

    def histories_url(self, obj):
        from srt.reports.models import History
        return self.get_url(History, singular='history', plural='histories', report=obj.id)
    histories_url.short_description = 'Histories'
