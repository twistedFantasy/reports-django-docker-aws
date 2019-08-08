import os

from django.db import models
from model_utils.choices import Choices
from fernet_fields import EncryptedTextField

from srt.reports.models import Report
from srt.core.models import BaseModel, STATUS


KIND = Choices(('s3', 'S3'), ('ftp', 'FTP'), ('sftp', 'SFTP'), ('email', 'Email'))


class Target(BaseModel):
    name = models.CharField('Name', max_length=64, db_index=True)
    kind = models.CharField('Kind', max_length=32, choices=KIND, default=KIND.s3, db_index=True)
    host = models.CharField('Host', max_length=128, blank=True, null=True,
        help_text="FTP or SFTP host")
    username = models.CharField('Username', max_length=128, blank=True, null=True,
        help_text="For S3, this is your access key")
    password = EncryptedTextField('Password', max_length=256, blank=True, null=True,
        help_text="For S3, this is your secret")
    path = models.CharField('Path', max_length=256, blank=True, null=True,
        help_text="For S3, this starts with your bucket")
    emails = models.CharField('Emails', max_length=128, blank=True, null=True,
        help_text="Comma-delimited list of email addresses")
    include_attachment = models.BooleanField('Include attachment', default=False)
    notes = models.TextField('Notes', default='', blank=True)

    class Meta:
        app_label = 'deliveries'
        verbose_name_plural = 'Targets'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} (target {self.id})'


class Delivery(BaseModel):
    target = models.ForeignKey(Target, on_delete=models.SET_NULL, blank=True, null=True)
    report = models.ForeignKey(Report, on_delete=models.SET_NULL, blank=True, null=True)
    path = models.CharField('Path', max_length=256, blank=True, null=True,
        help_text="For S3, this starts with your bucket")
    is_active = models.BooleanField('Is Active', default=True)
    notes = models.TextField('Notes', default='', blank=True)

    class Meta:
        app_label = 'deliveries'
        verbose_name_plural = 'Deliveries'
        ordering = ['-id']

    def __str__(self):
        return f'delivery_{self.id}'

    @property
    def fullpath(self):
        return os.path.join(self.target.path or '/', self.path or '')

    @property
    def where(self):
        WHERE = {
            's3': self.target.path,
            'ftp': self.target.host,
            'sftp': self.target.host,
            'email': self.target.emails,
        }
        return WHERE[self.target.kind]

    @property
    def task(self):
        from srt.deliveries.tasks.email import EmailTransport
        from srt.deliveries.tasks.ftp import FtpTransport
        from srt.deliveries.tasks.s3 import S3Transport
        from srt.deliveries.tasks.sftp import SftpTransport
        TRANSPORTS = {
            's3': S3Transport(),
            'ftp': FtpTransport(),
            'sftp': SftpTransport(),
            'email': EmailTransport(),
        }
        return TRANSPORTS[self.target.kind]

    @staticmethod
    def deliver(report_history):
        for delivery in Delivery.objects.filter(report_id=report_history.report_id, is_active=True):
            History.launch(report_history, delivery)


class History(BaseModel):
    from srt.reports.models import History as ReportHistory
    history = models.ForeignKey(ReportHistory, null=True, on_delete=models.SET_NULL)
    delivery = models.ForeignKey(Delivery, null=True, on_delete=models.SET_NULL)
    status = models.CharField('Status', max_length=16, choices=STATUS, default=STATUS.pending,
        db_index=True)
    url = models.URLField('URL', max_length=256, null=True, blank=True)
    msg = models.TextField('msg', null=True, blank=True)
    task_id = models.CharField('task_id', max_length=128, null=True)

    class Meta:
        app_label = 'deliveries'
        verbose_name_plural = 'History'
        ordering = ['-id']

    @classmethod
    def launch(cls, report_history, delivery, **kw):
        history = cls(**kw)
        history.history = report_history
        history.delivery = delivery
        history.save()

        # launch
        history.task_id = delivery.task.delay({'history-id': history.id}).task_id
        history.save(update_fields=['task_id'])
        return history
