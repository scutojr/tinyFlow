import mongoengine as me

from wf.utils import now_ms


INFO = 'info'
WARNING = 'warning'
ERROR = 'error'
FATAL = 'fatal'


class LogProcessor(me.EmbeddedDocument):

    content = me.ListField()

    def log(self, msg, time_ms=0, level=INFO, phase=''):
        self.content.append([
            time_ms or now_ms(),
            level,
            phase,
            msg
        ])

    def info(self, msg, phase=''):
        self.log(msg, level=INFO, phase=phase)

    def warning(self, msg, phase=''):
        self.log(msg, level=WARNING, phase=phase)

    def error(self, msg, phase=''):
        self.log(msg, level=ERROR, phase=phase)

    def fatal(self, msg, phase=''):
        self.log(msg, level=FATAL, phase=phase)

    def system(self, msg, level=INFO):
        self.log(msg, level=level, phase='system')
