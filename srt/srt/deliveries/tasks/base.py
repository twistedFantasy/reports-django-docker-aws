import os
import shutil
import tempfile

from box import Box
from celery import Task
from django.conf import settings

from srt.core.s3 import S3
from srt.core.models import STATUS
from srt.core.helpers import get_logger

logger = get_logger(__name__)


class Transport(Task):
    abstract = True

    def run(self, params):
        state = self.configure(params)
        dir = tempfile.mkdtemp()
        try:
            self.update(state, STATUS.processing)
            self.prepare(state, dir)
            self.deliver(state)
            self.update(state, STATUS.completed, 'delivered to %s' % self.destination(state))
        except Exception as e:
            self.update(state, STATUS.failed, msg=e)
        finally:
            shutil.rmtree(dir, ignore_errors=True)

    def configure(self, params):
        from srt.deliveries.models import History
        state = Box(history=History.objects.get(id=params['history-id']))
        state.delivery = state.history.delivery
        state.report_history = state.history.history
        state.url = getattr(state.report_history, 'path')
        state.remote = state.delivery.fullpath
        state.remote_dir = os.path.dirname(state.remote)
        state.filename = os.path.basename(state.remote)
        return state

    def update(self, state, status=None, msg=''):
        params = {**{'msg': msg}, **{'status': status}} if status else {}
        for field, value in params.items():
            setattr(state.history, field, value)
        state.history.save(update_fields=list(params))

    def prepare(self, state, dir):
        self.update(state, msg='preparing')
        state.local = os.path.join(dir, state.filename)
        bucket, env, remote = self.extract_s3_parts(state.url)
        s3 = S3(settings.AWS_KEY, settings.AWS_SECRET, bucket, env)
        s3.download(state.local, remote)

    def extract_s3_parts(self, s3url):
        values = s3url.replace('https://', '').replace('http://', '').replace('.s3.amazonaws.com', '').split('/')
        bucket, dir, s3path = values[0], values[1], '/'.join(values[2:])
        return bucket, dir, s3path

    def deliver(self, state):
        raise NotImplementedError()

    @staticmethod
    def destination(state):
        raise NotImplementedError()
