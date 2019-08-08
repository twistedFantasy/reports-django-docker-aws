from srt.deliveries.tasks.base import Transport
from srt.core.manage import register


@register()
class SftpTransport(Transport):
    abstract = False

    def deliver(self, state):
        pass

    @staticmethod
    def destination(state):
        return 'Not Implemented'
