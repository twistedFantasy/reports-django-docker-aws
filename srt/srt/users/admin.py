from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from srt.users.models import User


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = ['email', 'full_name', 'is_active', 'modified']
    list_filter = ['is_staff', 'is_superuser']
    search_fields = ['email', 'full_name']
    readonly_fields = ['created', 'modified']
    fieldsets = [
        (None, {'fields': ['email', 'password', 'full_name']}),
        ('Permissions', {'fields': ['is_active', 'is_staff', 'is_superuser']}),
        ('System', {'classes': ['collapse'], 'fields': ['created', 'modified']}),
    ]
    add_fieldsets = [
        (None, {
            'classes': ['wide'],
            'fields': ['email', 'password1', 'password2']}
         ),
    ]
    ordering = ['-modified']
    filter_horizontal = []
    show_full_result_count = False


admin.site.unregister(Group)
