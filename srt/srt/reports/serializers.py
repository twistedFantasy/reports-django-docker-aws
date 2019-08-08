from rest_framework.serializers import ModelSerializer, Serializer, CharField, EmailField

from srt.reports.models import Report, History


class ReportSerializer(ModelSerializer):

    class Meta:
        model = Report
        fields = ['id', 'uid', 'name', 'description', 'params']


class HistorySerializer(ModelSerializer):

    class Meta:
        model = History
        fields = ['id', 'report', 'status', 'path', 'params', 'msg', 'task_id']
