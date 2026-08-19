import logging
import mimetypes
import smtplib

from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from pathlib import Path
from typing import Any, Optional

from jinja2 import (
    Environment,
    FileSystemLoader,
    TemplateNotFound,
)

from app.config.settings import settings


logger = logging.getLogger(__name__)


class EmailService:
    """
    Email infrastructure service.

    Responsibilities:
    - Render Jinja2 templates
    - Build MIME emails
    - Attach files
    - Send emails through SMTP

    This service does NOT know about Celery,
    database models.
    """

    def __init__(self, templates_dir: Optional[Path] = None,):
        self.templates_dir = (templates_dir or settings.email_templates_dir)
        self.email_enabled = settings.email_enabled
        self.smtp_host = settings.email_host
        self.smtp_port = settings.email_port
        self.smtp_user = settings.email_user
        self.smtp_pass = settings.email_pass
        self.from_email = (settings.email_from or settings.email_user)
        self.from_name = settings.email_from_name

        try:
            self.jinja_env = Environment(
                loader=FileSystemLoader(
                    str(self.templates_dir)
                ),
                autoescape=True,
            )
        except Exception as exc:
            logger.warning(
                "Failed to initialize email templates: %s",
                exc,
            )
            self.jinja_env = None

    # ==========================================================
    # Template Rendering
    # ==========================================================

    def render_template(self,template_name: str,context: dict[str, Any],) -> str:

        if not self.jinja_env:
            raise RuntimeError(
                "Jinja2 environment is not initialized"
            )

        try:
            template = self.jinja_env.get_template(template_name)

            return template.render(context)

        except TemplateNotFound:
            logger.error(
                "Email template not found: %s",
                template_name,
            )
            raise

        except Exception:
            logger.exception(
                "Error rendering email template: %s",
                template_name,
            )
            raise

    # ==========================================================
    # Validate Attachment
    # ==========================================================

    @staticmethod
    def _validate_attachment(attachment: str | Path,) -> Path:

        path = Path(attachment)

        if not path.exists():
            raise FileNotFoundError(
                f"Email attachment not found: {path}"
            )

        if not path.is_file():
            raise ValueError(
                f"Email attachment is not a file: {path}"
            )

        if path.stat().st_size == 0:
            raise ValueError(
                f"Email attachment is empty: {path}"
            )

        return path

    # ==========================================================
    # Attach File
    # ==========================================================

    @staticmethod
    def _attach_file(message: MIMEMultipart,file_path: Path,) -> None:

        content_type, _ = mimetypes.guess_type(file_path.name)

        if content_type:
            maintype, subtype = content_type.split(
                "/",
                1,
            )
        else:
            maintype = "application"
            subtype = "octet-stream"

        with file_path.open("rb") as file:
            file_data = file.read()

        attachment = MIMEApplication(
            file_data,
            _subtype=subtype,
        )

        attachment.add_header(
            "Content-Disposition",
            "attachment",
            filename=file_path.name,
        )

        message.attach(attachment)

    # ==========================================================
    # Send Email
    # ==========================================================

    def send_email(
        self,
        *,
        to_email: str,
        subject: str,
        html_content: str,
        plain_text: Optional[str] = None,
        reply_to: Optional[str] = None,
        attachments: Optional[list[str | Path]] = None,
    ) -> bool:

        if not self.email_enabled:
            logger.warning(
                "Email disabled. Not sending to %s",
                to_email,
            )
            return False

        if not all(
            [
                self.smtp_host,
                self.smtp_user,
                self.smtp_pass,
            ]
        ):
            logger.error(
                "Email configuration is incomplete"
            )
            return False

        try:
            message = MIMEMultipart("mixed")

            message["From"] = (f"{self.from_name} <{self.from_email}>")

            message["To"] = to_email
            message["Subject"] = subject
            if reply_to:
                message["Reply-To"] = reply_to

            # --------------------------------------------------
            # Email body
            # --------------------------------------------------

            body = MIMEMultipart("alternative")

            if plain_text:
                body.attach(
                    MIMEText(
                        plain_text,
                        "plain",
                        "utf-8",
                    )
                )

            body.attach(
                MIMEText(
                    html_content,
                    "html",
                    "utf-8",
                )
            )

            message.attach(body)

            # --------------------------------------------------
            # Attachments
            # --------------------------------------------------

            for attachment in attachments or []:

                file_path = self._validate_attachment(
                    attachment
                )

                logger.info(
                    "Attaching file %s to email for %s",
                    file_path,
                    to_email,
                )

                self._attach_file(
                    message,
                    file_path,
                )

            # --------------------------------------------------
            # SMTP Server
            # --------------------------------------------------

            with smtplib.SMTP(self.smtp_host,self.smtp_port,timeout=30,) as server:

                server.starttls()

                server.login(
                    self.smtp_user,
                    self.smtp_pass,
                )

                server.send_message(message)

            logger.info(
                "Email sent successfully to %s",
                to_email,
            )

            return True

        except smtplib.SMTPAuthenticationError:
            logger.exception(
                "SMTP authentication failed"
            )
            return False

        except smtplib.SMTPException:
            logger.exception(
                "SMTP error while sending email to %s",
                to_email,
            )
            return False

        except Exception:
            logger.exception(
                "Error sending email to %s",
                to_email,
            )
            return False

    # ==========================================================
    # Send From Template
    # ==========================================================

    def send_from_template(
        self,
        *,
        to_email: str,
        subject: str,
        template_name: str,
        context: dict[str, Any],
        plain_text_template: Optional[str] = None,
        reply_to: Optional[str] = None,
        attachments: Optional[
            list[str | Path]
        ] = None,
    ) -> bool:

        try:
            html_content = self.render_template(
                template_name,
                context,
            )

            plain_text = None

            if plain_text_template:
                plain_text = self.render_template(
                    plain_text_template,
                    context,
                )

            return self.send_email(
                to_email=to_email,
                subject=subject,
                html_content=html_content,
                plain_text=plain_text,
                reply_to=reply_to,
                attachments=attachments,
            )

        except Exception:
            logger.exception(
                "Failed to send template email to %s",
                to_email,
            )
            return False
