from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.template import Context, Template
from django.utils import timezone
from loguru import logger
from pytracking.html import adapt_html

from config import celery_app
from prismvio.system.models import EmailTemplate

User = get_user_model()


@celery_app.task()
def get_users_count():
    """A pointless Celery task to demonstrate usage."""
    return User.objects.count()


@celery_app.task()
def send_email_verification_otp_by_email_template(
    email=None,
    action="verification step",
    otp="",
    timeout=120,
):
    if email is None:
        logger.error("Task send_email_verification_otp_by_email_template error: required email")
        return
    if otp is None:
        logger.error("Task send_email_verification_otp_by_email_template error: otp")
        return
    email_templates = EmailTemplate.objects.filter(code="000C")
    timeout = str(round(timeout / 60))
    if email_templates.exists() is True:
        email_template = email_templates.last()
        data = {
            "action": action,
            "code": otp,
            "timeout": timeout,
        }
        extra_data = {
            "user_email": email,
            "action": action,
            "email_template": email_template.name,
            "datetime_send": timezone.now().strftime("%Y/%m/%d, %H:%M:%S"),
            "code": otp,
        }
        context = Context(data)
        template = Template(email_template.html)
        html_content = template.render(context)
        new_html_email_text = adapt_html(
            html_content,
            extra_metadata=extra_data,
            click_tracking=True,
            open_tracking=True,
            base_open_tracking_url=f'{settings.BASE_URL.strip("/")}/open/',
        )

        title = "Vio Verification Code"
        send_mail(
            title,
            "",
            settings.EMAIL_HOST_USER,
            [email],
            html_message=new_html_email_text,
        )


@celery_app.task(bind=True)
def invite_new_user(self, **kwargs):
    emails: list = kwargs.get("emails")
    phones: list = kwargs.get("phones")
    if emails:
        email_templates = EmailTemplate.objects.filter(name="invite_vio_account")
        if email_templates.exists() is True:
            email_template = email_templates.last()
            title = "Invite create vio account"
            for email in emails:
                send_mail(title, "", settings.EMAIL_HOST_USER, [email], html_message=email_template.html)
    if phones:
        return None
