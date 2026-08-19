from typing import Any,Optional

from app.celery_app import celery_app
from app.database.database import SessionLocal
from app.config.settings import settings
from app.mailer.mailer import EmailService

from app.utils.logger import logger

TASK_MAX_RETRIES = 3
TASK_RETRY_DELAY_SECONDS = 60

#On boarding Mail task
@celery_app.task(name="app.tasks.onboarding_email_task",bind=True, max_retries=TASK_MAX_RETRIES, default_retry_delay = TASK_RETRY_DELAY_SECONDS,)

def onboarding_email_task(self,to_email: str,user_name: str,) -> bool:
    
    try :
        service = EmailService()
        context = {
            "user_name": user_name,
            "app_name": settings.app_name,
        }
        sent = service.send_from_template(
            to_email=to_email,
            subject=f"Welcome to {settings.app_name}!",
            template_name="welcome.html",
            context=context,
            plain_text_template="welcome.txt",
        )

        if not sent:
            raise RuntimeError(
                f"Failed to send welcome email to {to_email}"
            )

        return True

    except Exception as exc:
        logger.exception(
            "Welcome email task failed for %s",
            to_email,
        )

        raise self.retry(exc=exc)