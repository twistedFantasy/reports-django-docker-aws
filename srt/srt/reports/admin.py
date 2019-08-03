import os

from django import forms
from django.urls import reverse
from django.contrib import admin
from django.contrib.admin.helpers import ActionForm

from srt.reports.models import Report, History
from srt.reports.mixins import ReportAdminMixin
from srt.core.decorators import message_user


class ReportActionForm(ActionForm):
    start = forms.DateField(required=False)
    end = forms.DateField(required=False)


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin, ReportAdminMixin):
    action_form = ReportActionForm
    list_display = ['name']
    search_fields = ['name', 'description']
    readonly_fields = ['histories_url']
    fieldsets = [
        (None, {'fields': ['uid', 'name', 'description', 'params', 'histories_url']})
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
class HistoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'report', 'status']
    search_fields = ['report']
    readonly_fields = ['task_id']
    fieldsets = [
        (None, {'fields': ['report', 'status', 'path', 'params', 'msg', 'task_id']})
    ]
    ordering = ['-id']
    filter_horizontal = []
    list_select_related = ['report']
