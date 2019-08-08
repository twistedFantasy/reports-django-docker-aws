from srt.reports.tasks.report1 import Report1
from srt.core.manage import register


@register()
class Report2(Report1):
    abstract = False


if __name__ == '__main__':
    job = Report2()
    job.run()
