from django import forms
from django.contrib import admin

from srt.deliveries.models import Target, Delivery, History, KIND
from srt.deliveries.mixins import TargetAdminMixin, HistoryAdminMixin, DeliveryAdminMixin
from srt.core.decorators import message_user
from srt.core.codemirror2 import json_widget, python_widget


JSON_WIDGET = json_widget(readonly=True)
PYTHON_WIDGET = python_widget(readonly=True)


class TargetForm(forms.ModelForm):
    password = forms.CharField(label='Password', required=False, widget=forms.PasswordInput(render_value=True))


@admin.register(Target)
class TargetAdmin(admin.ModelAdmin, TargetAdminMixin):
    form = TargetForm
    list_display = ['name', 'kind', 'path', 'deliveries_url']
    list_filter = ['kind']
    search_fields = ['name', 'notes']
    readonly_fields = ['deliveries_url', 'created', 'modified']
    fieldsets = [
        (None, {'fields': ['name']}),
        ('Details', {'fields': ['kind', 'host', 'username', 'password', 'path', 'emails']}),
        ('Delivery', {'fields': ['deliveries_url']}),
        ('System', {'classes': ['collapse'], 'fields': [
            'notes', 'created', 'modified',
        ]}),
    ]
    add_fieldsets = [
        (None, {'classes': ['wide'], 'fields': ['kind']}),
    ]
    conditional_fieldsets = {
        'kind': {
            KIND.s3: {'Details': ['kind', 'username', 'password', 'path']},
            KIND.ftp: {'Details': ['kind', 'host', 'username', 'password', 'path']},
            KIND.sftp: {'Details': ['kind', 'host', 'username', 'password', 'path']},
            KIND.email: {'Details': ['kind', 'emails', 'include_attachment']},
        }
    }
    ordering = ['name']
    filter_horizontal = []


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin, DeliveryAdminMixin):
    list_display = ['id', 'report_url', 'target_url', 'where', 'delivered_url']
    search_fields = ['notes']
    readonly_fields = ['delivered_url', 'created', 'modified']
    fieldsets = [
       (None, {'fields': ['report', 'target', 'is_active']}),
       ('Details', {'fields': ['path']}),
       ('Delivery', {'fields': ['delivered_url']}),
       ('System', {'classes': ['collapse'], 'fields': [
           'notes', 'created', 'modified',
       ]}),
    ]
    add_fieldsets = [
       (None, {'classes': ['wide'], 'fields': ['report', 'target']}),  # noqa
    ]
    ordering = ['-id']
    filter_horizontal = []


class HistoryForm(forms.ModelForm):
    msg = forms.CharField(required=False, widget=PYTHON_WIDGET)


@admin.register(History)
class HistoryAdmin(admin.ModelAdmin, HistoryAdminMixin):
    form = HistoryForm
    list_display = ['id', 'history_url', 'status', 'modified']
    list_filter = ['status']
    search_fields = ['msg']
    readonly_fields = ['history_url', 'delivery_url', 'status', 'file_url', 'task_id', 'created', 'modified']
    fieldsets = [
        (None, {'fields': ['history_url', 'delivery_url']}),
        ('Status', {'fields': ['status', 'msg']}),
        ('Data', {'fields': ['file_url']}),
        ('System', {'classes': ['collapse'], 'fields': [
            'task_id', 'created', 'modified',
        ]}),
    ]
    ordering = ['-id']
    filter_horizontal = []
    show_full_result_count = False
    actions = ['relaunch']

    class Media:
        css = {'all': ['css/save-no-add.css']}

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('history__report')

    def has_add_permission(self, request):
        return False

    @message_user("Launched selected deliveries")
    def relaunch(self, request, queryset):
        for history in queryset:
            History.launch(history.history, history.delivery)
    relaunch.short_description = 'Relaunch deliveries'
