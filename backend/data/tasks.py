from django.db.transaction import atomic

from huey.signals import SIGNAL_CANCELED, SIGNAL_COMPLETE, SIGNAL_ERROR, \
    SIGNAL_EXECUTING, SIGNAL_EXPIRED, SIGNAL_LOCKED, SIGNAL_RETRYING, \
    SIGNAL_REVOKED, SIGNAL_SCHEDULED, SIGNAL_INTERRUPTED
from huey.contrib.djhuey import on_startup, signal

from .models import HueyTask


FINISHED_SIGNALS = [
    SIGNAL_CANCELED,
    SIGNAL_COMPLETE,
    # SIGNAL_ERROR, # this one can be retried
    SIGNAL_EXPIRED,
    SIGNAL_REVOKED,
    SIGNAL_INTERRUPTED
]


@signal()
def signal_handler(signal, task, exc=None):
    with atomic():
        # finished is only when task is in FINISHED_SIGNALS or SIGNAL_ERROR without retries
        finished = (signal == SIGNAL_ERROR and task.retries is not None and task.retries == 0) or (signal in FINISHED_SIGNALS)
        HueyTask.objects.create(
            uuid=task.id, name=task.name, signal=signal, is_finished=finished,
            error=exc, retries_left=task.retries
        )
