from django_filters.rest_framework import FilterSet, CharFilter

from srt.users.models import User
from srt.core.filters import ObjectFieldFilterBackend


class UserFilter(FilterSet):
    name = CharFilter(field_name='full_name', lookup_expr='icontains')

    class Meta:
        model = User
        fields = ['email', 'name', 'full_name']


class UserFilterBackend(ObjectFieldFilterBackend):
    filter_field = 'user__id'
