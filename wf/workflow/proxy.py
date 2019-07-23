import sys
from threading import local


_wf = local()
_log = local()
_tri = local()


class TriggerChain(object):
    @property
    def request(self):
        return _tri.trigger.request

    @property
    def event(self):
        return _tri.trigger.event

    @property
    def judgement(self):
        return _tri.trigger.judgement


class Logger(object):
    def log(self, msg, phase='', level=''):
        _log.logger.log(msg, phase=phase, level=level)

    def info(self, msg, phase=''):
        _log.logger.info(msg, phase=phase)

    def warning(self, msg, phase=''):
        _log.logger.warning(msg, phase=phase)

    def error(self, msg, phase=''):
        _log.logger.error(msg, phase=phase)

    def fatal(self, msg, phase=''):
        _log.logger.fatal(msg, phase=phase)


class WorkflowProxy(Logger, TriggerChain):
    def set_workflow(self, wf):
        _wf.workflow = wf
        _log.logger = wf.logger
        _tri.trigger = wf.tri_chain

    def clear(self):
        _wf.workflow = None
        _log.logger = None
        _tri.trigger = None

    def goto(self, next_task_name, reason=None):
        return _wf.workflow.goto(next_task_name, reason)

    def wait(self, event, to_state, on_fired='', on_timeout='', timeout_ms=sys.maxint):
        return _wf.workflow.wait(
            event, to_state,
            on_fired=on_fired,
            on_timeout=on_timeout,
            timeout_ms=timeout_ms
        )

    def ask(self, desc, options, on_fired):
        return _wf.workflow.ask(desc, options, on_fired)

    def end(self):
        return _wf.workflow.end()

    def get_prop(self, key, default=None):
        return _wf.workflow.get_prop(key, default=default)

    def set_prop(self, key, value):
        return _wf.workflow.set_prop(key, value)

    @property
    def name(self):
        return _wf.workflow.name

    @property
    def trigger(self):
        return trigger

    @property
    def logger(self):
        return logger


logger = Logger()
trigger = TriggerChain()
wf_proxy = WorkflowProxy()
