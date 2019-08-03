import csv
import uuid

from django.conf import settings
from celery import Task

from srt.users.models import User
from srt.reports.models import History, STATUS
from srt.core.manage import register


@register()
class Report2(Task):
    abstract = False

    def run(self, history_id, start_date, end_date, *args, **kwargs):
        try:
            history = self.get_history(history_id)
            history.modify(status=STATUS.processing)
            path = "s3_url"  # FIXME: upload to S3
            history.modify(path=path, status=STATUS.completed)
        except Exception as e:
            history.modify(msg=str(e), status=STATUS.failed)

    def get_history(self, id):
        return History.objects.get(id=id)


if __name__ == '__main__':
    job = Report2()
    job.run()
