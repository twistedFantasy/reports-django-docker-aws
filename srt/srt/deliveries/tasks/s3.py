from srt.deliveries.tasks.base import Transport
from srt.core.manage import register
from srt.core.s3 import S3


@register()
class S3Transport(Transport):
    abstract = False

    def deliver(self, state):
        bucket, *remote = state.remote.strip('/').split('/', 1)
        s3 = S3(state.delivery.target.username, state.delivery.target.password, bucket)
        s3.upload(state.local, remote[0])

    @staticmethod
    def destination(state):
        return 'S3: {state.remote}'.format(state=state)
