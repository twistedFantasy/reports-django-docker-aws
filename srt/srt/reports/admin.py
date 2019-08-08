from django import forms
from django.contrib import admin
from django.contrib.admin.helpers import ActionForm

from srt.reports.models import Report, History
from srt.reports.mixins import ReportAdminMixin, HistoryAdminMixin
from srt.core.decorators import message_user
from srt.core.codemirror2 import json_widget, python_widget


JSON_WIDGET = json_widget(readonly=False)
PYTHON_WIDGET = python_widget(readonly=True)


class ReportActionForm(ActionForm):
    start = forms.DateField(required=False)
    end = forms.DateField(required=False)


class ReportForm(forms.ModelForm):
    params = forms.CharField(required=False, widget=JSON_WIDGET)


class HistoryForm(forms.ModelForm):
    params = forms.CharField(required=False, widget=JSON_WIDGET)
    msg = forms.CharField(required=False, widget=PYTHON_WIDGET)


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin, ReportAdminMixin):
    action_form = ReportActionForm
    form = ReportForm
    list_display = ['name']
    search_fields = ['name', 'description']
    readonly_fields = ['histories_url', 'created', 'modified']
    fieldsets = [
        (None, {'fields': ['uid', 'name', 'description', 'params', 'histories_url']}),
        ('System', {'classes': ['collapse'], 'fields': ['created', 'modified']}),
    ]
    ordering = ['name']
    filter_horizontal = []
    actions = ['launch']

    @message_user("Launched selected reports")
    def launch(self, request, queryset):
        start, end = request.POST['start'], request.POST['end']
        for report in queryset:
            report.launch(start, end)
    launch.short_description = 'Launch reports'


@admin.register(History)
class HistoryAdmin(admin.ModelAdmin, HistoryAdminMixin):
    form = HistoryForm
    list_display = ['id', 'report', 'status']
    list_filter = ['status']
    search_fields = ['report']
    readonly_fields = ['path_url', 'task_id', 'created', 'modified']
    fieldsets = [
        (None, {'fields': ['report', 'status', 'path_url', 'params', 'msg', 'task_id']}),
        ('System', {'classes': ['collapse'], 'fields': ['created', 'modified']}),
    ]
    ordering = ['-id']
    filter_horizontal = []
    list_select_related = ['report']

    def has_add_permission(self, request):
        return False
