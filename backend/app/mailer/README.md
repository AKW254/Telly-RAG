# Reusable Email Mailer System

A production-ready, async-first email service with Jinja2 template support and Celery integration. Designed to be easily portable to other projects.

## Features

- **Async Email Sending**: Celery-based queue for non-blocking email dispatch
- **Template Support**: Jinja2 templates for professional, customizable emails
- **Fallback Support**: Works with or without Celery (graceful degradation)
- **Retry Logic**: Automatic retry with configurable delays
- **SMTP Compatibility**: Works with any SMTP server (Gmail, SendGrid, custom servers)
- **Type Safe**: Full type hints for IDE autocomplete
- **Reusable**: Minimal dependencies, easy to copy to other projects

## Configuration

Add to your `.env` file:

```env
# Email Settings
EMAIL_ENABLED=true
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your-email@gmail.com
EMAIL_PASS=your-app-password
EMAIL_FROM=noreply@yourapp.com
EMAIL_FROM_NAME=Your App Name
```

## Usage

### Automatic Email Sending (Recommended)

```python
from app.mailer import send_welcome_email, send_password_reset_email

# Send welcome email (automatically queued in Celery)
send_welcome_email(
    to_email="user@example.com",
    user_name="John Doe",
    activation_link="https://yourapp.com/activate/token"
)

# Send password reset email
send_password_reset_email(
    to_email="user@example.com",
    user_name="John Doe",
    reset_link="https://yourapp.com/reset/token"
)

# Send generic notification
from app.mailer import send_notification_email

send_notification_email(
    to_email="user@example.com",
    user_name="John Doe",
    notification_title="Job Match Found!",
    notification_message="We found 3 jobs matching your preferences",
    action_url="https://yourapp.com/jobs",
    action_label="View Jobs"
)
```

### Direct Service Usage (For Custom Templates)

```python
from app.mailer.mailer import EmailService

service = EmailService()

# Render and send from custom template
html = service.render_template("custom_email.html", {
    "user_name": "John",
    "custom_data": "value"
})

service.send_email(
    to_email="user@example.com",
    subject="Custom Email",
    html_content=html
)

# Or use convenience method
service.send_from_template(
    to_email="user@example.com",
    subject="Custom Email",
    template_name="custom_email.html",
    context={"user_name": "John"}
)
```

### Queue Tasks Directly

```python
from app.tasks import send_generic_email_task

# Queue custom email task
send_generic_email_task.delay(
    to_email="user@example.com",
    subject="Custom Subject",
    template_name="my_template.html",
    context={"name": "John", "data": "value"}
)
```

## Project Structure

```
app/mailer/
├── __init__.py              # Public API exports
├── mailer.py                # EmailService class and convenience functions
└── templates/
    ├── welcome.html         # Welcome email template
    ├── password_reset.html   # Password reset template
    └── notification.html     # Generic notification template

app/tasks/
└── mailer_tasks.py          # Celery async tasks
```

## Creating Custom Templates

Add new template files to `app/mailer/templates/`:

```html
<!-- app/mailer/templates/custom.html -->
<!DOCTYPE html>
<html>
<head>
    <title>{{ title }}</title>
</head>
<body>
    <h1>Hello {{ user_name }}!</h1>
    <p>{{ message }}</p>
    {% if action_url %}
    <a href="{{ action_url }}">{{ action_label }}</a>
    {% endif %}
</body>
</html>
```

Send emails with your custom template:

```python
from app.mailer.mailer import EmailService

service = EmailService()
service.send_from_template(
    to_email="user@example.com",
    subject="Custom Subject",
    template_name="custom.html",
    context={
        "user_name": "John",
        "title": "Important Update",
        "message": "Here's an update for you.",
        "action_url": "https://app.com/action",
        "action_label": "Click Here"
    }
)
```

## Porting to Other Projects

To use this mailer in another project:

1. **Copy files**:
   ```bash
   # Copy mailer module
   cp -r app/mailer/ your-project/app/

   # Copy mailer tasks
   cp app/tasks/mailer_tasks.py your-project/app/tasks/
   ```

2. **Update settings** (add to your settings class):
   ```python
   email_host: str | None = None
   email_port: int = 587
   email_user: str | None = None
   email_pass: str | None = None
   email_from: str | None = None
   email_from_name: str = "Your App Name"
   email_enabled: bool = False
   email_templates_dir: Path = BASE_DIR / "app" / "mailer" / "templates"
   ```

3. **Update Celery app** (in your celery_app.py):
   ```python
   celery_app = Celery(
       "your-app",
       broker=settings.celery_broker_url,
       backend=settings.celery_result_backend,
       include=["app.tasks.mailer_tasks"],  # Add this
   )
   ```

4. **Configure environment** (in your .env):
   ```env
   EMAIL_ENABLED=true
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USER=your-email@gmail.com
   EMAIL_PASS=your-app-password
   EMAIL_FROM=noreply@yourapp.com
   EMAIL_FROM_NAME=Your App Name
   ```

5. **Use in your services**:
   ```python
   from app.mailer import send_welcome_email
   
   # Or directly from mailer_tasks for custom implementations
   from app.tasks.mailer_tasks import send_generic_email_task
   ```

## Error Handling

The mailer gracefully handles errors:

```python
# These won't crash your app if email config is missing
send_welcome_email(
    to_email="user@example.com",
    user_name="John"
)
# Returns False if email_enabled=False or config missing
# Logs warning and continues execution
```

Enable debug logging to troubleshoot:

```python
import logging
logging.getLogger("app.mailer.mailer").setLevel(logging.DEBUG)
```

## SMTP Server Configuration

### Gmail
```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your-email@gmail.com
EMAIL_PASS=your-16-digit-app-password
```
[Get Gmail App Password](https://support.google.com/accounts/answer/185833)

### SendGrid
```env
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USER=apikey
EMAIL_PASS=your-sendgrid-api-key
EMAIL_FROM=noreply@yourapp.com
```

### Custom SMTP Server
```env
EMAIL_HOST=mail.yourserver.com
EMAIL_PORT=587
EMAIL_USER=username
EMAIL_PASS=password
EMAIL_FROM=noreply@yourserver.com
```

## Celery Integration

The mailer works with or without Celery:

- **With Celery** (Recommended for production):
  - Emails are queued and sent asynchronously
  - Automatic retries on failure
  - Non-blocking request handling

- **Without Celery** (Development/fallback):
  - Emails sent synchronously
  - No retries
  - Requests block until email is sent

## Testing

Mock email service for testing:

```python
import pytest
from unittest.mock import patch
from app.mailer import send_welcome_email

@patch('app.mailer.mailer.EmailService.send_email')
def test_welcome_email(mock_send):
    mock_send.return_value = True
    result = send_welcome_email("test@example.com", "Test User")
    assert mock_send.called
```

## Troubleshooting

### Emails not sending
1. Check `EMAIL_ENABLED=true` in `.env`
2. Verify SMTP credentials
3. Check logs: `logging.getLogger("app.mailer.mailer").setLevel(logging.DEBUG)`
4. Ensure Celery worker is running (if using async)

### Templates not found
1. Verify template files exist in `app/mailer/templates/`
2. Check `EMAIL_TEMPLATES_DIR` setting points to correct path
3. Ensure template filenames match exactly

### Celery tasks not running
1. Start Celery worker: `celery -A app.celery_app worker -l info`
2. Check broker connection: `redis-cli ping`
3. Verify `CELERY_BROKER_URL` and `CELERY_RESULT_BACKEND` are set

## Dependencies

- `jinja2` - Template rendering
- `celery` - Async task queue (optional)
- `redis` - Celery broker (optional)
- Standard library `smtplib` - SMTP client


