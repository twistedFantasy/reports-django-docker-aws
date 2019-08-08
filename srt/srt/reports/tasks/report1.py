import os
import csv
import json
import uuid
import tempfile
import shutil

from django.conf import settings
from celery import Task

from srt.reports.models import Report, History, STATUS
from srt.core.manage import register
from srt.core.s3 import S3


@register()
class Report1(Task):
    abstract = False

    def run(self, history_id=None, report_id=None, *args, **kwargs):
        if report_id:
            history_id = self._beat(report_id)
        dir = tempfile.mkdtemp()
        try:
            history = self.get_history(history_id)
            history.modify(status=STATUS.processing)
            filename = f'{uuid.uuid4()}.csv'
            local = os.path.join(dir, filename)
            with open(local, mode='w') as file:
                writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                writer.writerow(['Full Name', 'system@gmail.com', 10])
            remote = os.path.join(f'report_{history.report.id}', filename)
            s3 = S3(settings.AWS_KEY, settings.AWS_SECRET, settings.AWS_BUCKET, settings.ENV)
            s3.upload(local, str(remote), public=True)
            self.deliver(history)
            history.modify(path=s3.get_url(remote), status=STATUS.completed)
        except Exception as e:
            history.modify(msg=str(e), status=STATUS.failed)
        finally:
            shutil.rmtree(dir, ignore_errors=True)

    def get_history(self, id):
        return History.objects.get(id=id)

    def _beat(self, report_id):
        report = Report.objects.get(id=report_id)
        params = json.dumps(json.loads(report.params or '{}'), indent=2, sort_keys=True)
        history = History(**{'report': report, 'params': params, 'task_id': self.request.id})
        history.save()
        return history.id

    def deliver(self, history):
        from srt.deliveries.models import Delivery
        Delivery.deliver(history)


if __name__ == '__main__':
    job = Report1()
    job.run()
