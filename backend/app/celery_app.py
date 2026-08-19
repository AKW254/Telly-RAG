from celery import Celery
from celery import signals

from app.config.settings import settings
from app.utils.logger import get_logger


celery_logger = get_logger("celery")


def _task_name(sender=None) -> str:
    return getattr(sender, "name", None) or getattr(sender, "__name__", None) or str(sender)


def _task_result_summary(result) -> str:
    summary = repr(result)
    if len(summary) > 200:
        return f"{summary[:197]}..."
    return summary


def _parse_bool(value) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() not in ("false", "0", "no", "")

celery_app = Celery(
    "Telly RAG",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        "app.tasks.mailer_tasks",
    ],
)

runtime_timezone = (
    settings.celery_timezone
    or "Africa/Nairobi"
)

celery_task_always_eager = (
    settings.environment.lower() == "development"
    or _parse_bool(settings.celery_task_always_eager)
)

celery_app.conf.update(
    # Serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",

    # Timezone
    timezone=runtime_timezone,
    enable_utc=False,

    # Broker reliability
    broker_connection_timeout=settings.celery_broker_connection_timeout,
    broker_connection_retry=True,
    broker_connection_retry_on_startup=True,
    broker_connection_max_retries=settings.celery_broker_connection_max_retries,

    # Worker behavior
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_track_started=True,

    # Time limits
    task_time_limit=1800,
    task_soft_time_limit=1500,

    # Development
    task_always_eager=celery_task_always_eager,
    task_eager_propagates=celery_task_always_eager,
    task_store_eager_result=celery_task_always_eager,

    # Redis/RabbitMQ transport
    broker_transport_options={
        "socket_connect_timeout":
            settings.celery_broker_connection_timeout,

        "socket_timeout":
            settings.celery_broker_connection_timeout,

        "retry_on_timeout": True,
    },
)


@signals.task_prerun.connect
def _log_task_start(sender=None, task_id=None, **kwargs):
    celery_logger.info("Task started: %s [%s]", _task_name(sender), task_id)


@signals.task_success.connect
def _log_task_success(sender=None, result=None, **kwargs):
    celery_logger.info(
        "Task succeeded: %s result=%s",
        _task_name(sender),
        _task_result_summary(result),
    )


@signals.task_failure.connect
def _log_task_failure(sender=None, task_id=None, exception=None, **kwargs):
    celery_logger.error(
        "Task failed: %s [%s] %s",
        _task_name(sender),
        task_id,
        exception,
    )


@signals.task_retry.connect
def _log_task_retry(sender=None, request=None, reason=None, **kwargs):
    task_id = getattr(request, "id", None)
    celery_logger.warning(
        "Task retrying: %s [%s] reason=%s",
        _task_name(sender),
        task_id,
        reason,
    )
