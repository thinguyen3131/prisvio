import logging
import time
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.db import transaction
from django.db.models import Q
from django.template import Context, Template
from django.utils import timezone

import pytz
from pytracking.html import adapt_html

# from celery_logs.utils import CeleryDatabaseLogger, inner_func_log_exceptions
# from core.celery import add_task
# from core.containers import get_container
# from core.utils import get_random_string, validate_phone_number
# from core.utils.constants import DEFAULT_USER_SETTINGS
# from events.models import Event
# from events.tasks import subscribe_to_google, subscribe_to_outlook
from prisvio.celery import app
# from prism.utils.time_utils import milliseconds
# from profiletemplate.models import Participant, ProfileTemplate
from system.enum import EmailTemplateLanguage, SystemConfigFolder, SystemConfigName
from system.models import  EmailTemplate #, SystemConfig, EmailLog
# from system.models.email_tracking import EmailTracking
from users.enums import UserTypeOption
# from users.models import UserInvite, UserSetting, UserSocialAuth

logger = logging.getLogger('django')
User = get_user_model()


# def _send_emails(celery_task, user_id, emails, msg, celery_logger, **kwargs):
#     """Send emails function"""
#     # With connection for sending few emails inside one connection(should be faster)
#     # used like separate function instead of send_mass for checking particular invite result
#     for email in emails:
#         with inner_func_log_exceptions(celery_task, logger):
#             try:
#                 # validating email
#                 validate_email(email)
#                 # check if user already in system
#                 User.objects.get(email=email)
#             except ValidationError:
#                 celery_logger.log({'validation_error': email})
#             except User.DoesNotExist:
#                 # get invitation object
#                 invite, created = UserInvite.objects.get_or_create(user_id=user_id, email_or_phone=email)
#                 logger.info(f'{email} not in database')
#                 current_date = datetime.now().replace(tzinfo=pytz.utc)
#                 # send if:
#                 # not sent yet OR created OR last_sent_time more that current on SEND_DELAY period
#                 if not invite.sent or created or invite.last_update + \
#                         timedelta(seconds=invite.SEND_DELAY) < current_date:  # noqa
#                     logger.info(f'Sending notification to {email}')
#                     title = kwargs.get('email_title')
#                     if settings.USE_SES:
#                         container = get_container()
#                         aws_ses_services = container.services.aws_ses_service()
#                         response, error = aws_ses_services.send_email(
#                             title,
#                             email,
#                             msg,
#                         )
#                         EmailLog.objects.create(
#                             email=email,
#                             subject=title,
#                             body=msg,
#                             response=response,
#                             error=error,
#                         )
#                     else:
#                         send_mail(
#                             title,
#                             '',
#                             settings.EMAIL_HOST_USER,
#                             [email],
#                             html_message=msg,
#                         )
#                     invite.sent = True
#                     invite.save()
#                 else:
#                     logger.info('Already sent')


# def _send_sms(celery_task, user_id, phones, msg):
#     """Send emails function"""
#     for phone in phones:
#         with inner_func_log_exceptions(celery_task, logger):
#             try:
#                 # check if user already in system
#                 User.objects.get(phone_number=phone)
#             except User.DoesNotExist:
#                 # get invitation object
#                 invite, created = UserInvite.objects.get_or_create(user_id=user_id, email_or_phone=phone)
#                 logger.info(f'{phone} not in database')
#                 current_date = datetime.now().replace(tzinfo=pytz.utc)
#                 # send if:
#                 # not sent yet OR created OR last_sent_time more that current on SEND_DELAY period
#                 if not invite.sent or created or invite.last_update + timedelta(
#                         seconds=invite.SEND_DELAY) < current_date:
#                     logger.info(f'Sending notification to {phone}')
#                     # sns_client.publish(PhoneNumber=phone, Message=msg)
#                     # use vietguy to handle this
#                     invite.sent = True
#                     invite.save()
#                 else:
#                     logger.info('Already sent')


# @app.task(bind=True)
# def invite_friends(self, user_id, data):
#     """Sending invitations for new or exist users by emails, phone number"""
#     with CeleryDatabaseLogger(self) as celery_logger:
#         emails = data.get('emails')
#         phones = data.get('phones')
#         link = data.get('link')

#         send_user = User.objects.get(id=user_id)
#         for email in emails:
#             try:
#                 target_user = User.objects.get(email=email)
#                 send_user.add_friend(user_id=target_user.id)
#             except User.DoesNotExist:
#                 logger.info(f'Can not find user with {email}')
#                 continue

#         email_templates = EmailTemplate.objects.filter(code='000D')
#         data = {
#             'full_name': send_user.full_name,
#             'link': link,
#         }
#         msg = (f'Hi, {send_user.full_name} wants '
#                f'to see you in a vio app, please follow: {link}')
#         if emails and email_templates.exists() is True:
#             email_template = email_templates.last()
#             context = Context(data)
#             template = Template(email_template.html)
#             html_content = template.render(context)

#             _send_emails(self,
#                          user_id,
#                          emails,
#                          html_content,
#                          celery_logger,
#                          email_title='Vio app invitation')
#         if phones:
#             _send_sms(self, user_id, phones, msg)


# @app.task(bind=True)
# def invite_new_user(self, **kwargs):
#     emails: list = kwargs.get('emails')
#     phones: list = kwargs.get('phones')
#     if emails:
#         email_templates = EmailTemplate.objects.filter(name='invite_vio_account')
#         if email_templates.exists() is True:
#             email_template = email_templates.last()
#             title = 'Invite create vio account'
#             for email in emails:
#                 if settings.USE_SES:
#                     container = get_container()
#                     aws_ses_services = container.services.aws_ses_service()
#                     response, error = aws_ses_services.send_email(
#                         title,
#                         email,
#                         email_template.html,
#                     )
#                     EmailLog.objects.create(
#                         email=email,
#                         subject=title,
#                         body=email_template.html,
#                         response=response,
#                         error=error,
#                     )
#                 else:
#                     send_mail(title,
#                               '',
#                               settings.EMAIL_HOST_USER,
#                               [email],
#                               html_message=email_template.html)
#     if phones:
#         # sms_templates = SMSTemplate.objects.filter(name='invite_vio_account')
#         # if sms_templates.exists() is True:
#         #     sms_template = sms_templates.last()
#         #     try:
#         #         for phone in phones:
#         #             sns_client.publish(
#         #                 PhoneNumber=phone,
#         #                 Message=sms_template.content.replace('{{user_mobile}}', phone),
#         #             )
#         #     except Exception as e:
#         #         logger.error(f'{str(e)}')
#         #     logger.info(f'Sent an invite create account to {phones}')
#         return None


# @app.task(bind=True)
# def renew_calendar_subscriptions(self, user_id):
#     user_social_auth = UserSocialAuth.objects.filter(user_id=user_id)
#     if user_social_auth.exists():
#         with CeleryDatabaseLogger(self):
#             for social in user_social_auth:
#                 if social is not None:
#                     sub_time = social.calendar_data.get('sub_time')
#                     if sub_time:
#                         current_time = milliseconds()
#                         exp_time = sub_time + social.SUBSCRIPTION_DURATION
#                         next_refresh = current_time + settings.SIMPLE_JWT[
#                             'ACCESS_TOKEN_LIFETIME_MILLI_SEC'
#                         ] + milliseconds(
#                             60 * 60)
#                         if exp_time > next_refresh:
#                             continue
#                     if social.provider == Event.PROVIDER_GOOGLE_OAUTH2:
#                         subscribe_to_google.delay(social.pk)
#                     elif social.provider == Event.PROVIDER_MICROSOFT_OAUTH2:
#                         subscribe_to_outlook.delay(social.pk)


# @app.task
# def invite_to_event_by_email_template(
#         email=None,
#         full_name=None,
#         title='',
#         main_image='',
#         start='',
#         end='',
#         full_location='',
#         location='',
# ):
#     if full_name is None:
#         logger.error('Task invite_event_to_user error: required full_name')
#         return
#     if email is None:
#         logger.error('Task invite_event_to_user error: required emails list')
#         return

#     email_templates = EmailTemplate.objects.filter(code='000B')
#     if email_templates.exists() is True:
#         email_template = email_templates.last()
#         data = {}
#         try:
#             """Existing user"""
#             user = User.objects.get(email=email)
#             data['name'] = user.full_name
#         except User.DoesNotExist:
#             """Non account user"""
#             data['name'] = 'guest'

#         data = {
#             **data,
#             'banner': main_image,
#             'event_name': title,
#             'time_from': start,
#             'time_to': end,
#             'location_name': full_location or '',
#             'location_address': location,
#             'link': 'https://prismtech.vn/',
#         }

#         context = Context(data)
#         template = Template(email_template.html)
#         html_content = template.render(context)
#         title = f'{full_name} invited you to {title}'
#         if settings.USE_SES:
#             container = get_container()
#             aws_ses_services = container.services.aws_ses_service()
#             response, error = aws_ses_services.send_email(
#                 title,
#                 email,
#                 html_content,
#             )
#             EmailLog.objects.create(
#                 email=email,
#                 subject=title,
#                 body=html_content,
#                 response=response,
#                 error=error,
#             )
#         else:
#             send_mail(
#                 title,
#                 '',
#                 settings.EMAIL_HOST_USER,
#                 [email],
#                 html_message=html_content,
#             )


@app.task
def send_email_verification_otp_by_email_template(
        email=None,
        action='verification step',
        otp='',
        timeout=120,
):
    if email is None:
        logger.error('Task send_email_verification_otp_by_email_template error: required email')
        return
    if otp is None:
        logger.error('Task send_email_verification_otp_by_email_template error: otp')
        return
    email_templates = EmailTemplate.objects.filter(code='000C')
    timeout = str(round(timeout / 60))
    if email_templates.exists() is True:
        email_template = email_templates.last()
        data = {
            'action': action,
            'code': otp,
            'timeout': timeout,
        }
        extra_data = {
            'user_email': email,
            'action': action,
            'email_template': email_template.name,
            'datetime_send': timezone.now().strftime('%Y/%m/%d, %H:%M:%S'),
            'code': otp,
        }
        context = Context(data)
        template = Template(email_template.html)
        html_content = template.render(context)
        new_html_email_text = adapt_html(
            html_content,
            extra_metadata=extra_data,
            click_tracking=True,
            open_tracking=True,
            base_open_tracking_url=f'{settings.BASE_URL.strip("/")}/open/')

        title = 'Vio Verification Code'
        send_mail(
            title,
            '',
            settings.EMAIL_HOST_USER,
            [email],
            html_message=new_html_email_text,
        )


# @app.task
# def send_email_user_report_to_by_email_template(
#         report_id='',
#         reporter='',
#         reporter_name='',
#         report_type='',
#         target_type='',
#         target='',
#         target_name='',
#         description='',
#         status='',
#         open_date='',
# ):
#     email_templates = EmailTemplate.objects.filter(code='000E')
#     if email_templates.exists() is True:
#         email_template = email_templates.last()
#         data = {
#             'report_id': report_id,
#             'reporter': reporter,
#             'reporter_name': reporter_name,
#             'report_type': report_type,
#             'target_type': target_type,
#             'target': target,
#             'target_name': target_name,
#             'description': description,
#             'status': status,
#             'open_date': open_date,
#         }

#         context = Context(data)
#         template = Template(email_template.html)
#         html_content = template.render(context)
#         title = f'Vio User Report ID #{report_id}'
#         emails = settings.EMAIL_ALIAS_RECEIVE_REPORT_FROM_USER
#         if settings.USE_SES:
#             container = get_container()
#             aws_ses_services = container.services.aws_ses_service()
#             for email in emails:
#                 response, error = aws_ses_services.send_email(
#                     title,
#                     email,
#                     html_content,
#                 )
#                 EmailLog.objects.create(
#                     email=email,
#                     subject=title,
#                     body=html_content,
#                     response=response,
#                     error=error,
#                 )
#         else:
#             send_mail(
#                 title,
#                 '',
#                 settings.EMAIL_HOST_USER,
#                 emails,
#                 html_message=html_content,
#             )


# def share_profile_via_email(profile_id: int, user_id: int, email: str, link: str):
#     if not email:
#         logger.error('Task share_via_email error: email is required')
#         return None
#     try:
#         user = User.objects.get(pk=user_id)
#     except User.DoesNotExist:
#         logger.info(f'The user does not exist. User ID: {user_id}')
#         return None
#     try:
#         profile = User.objects.get(pk=profile_id)
#     except User.DoesNotExist:
#         logger.info(f'The profile does not exist. User profile ID: {profile_id}')
#         return None

#     email_templates = EmailTemplate.objects.filter(
#         code='share_profile_via_email',
#         language=EmailTemplateLanguage.ENG.value,
#     )
#     if email_templates.exists() is True:
#         email_template = email_templates.last()

#         sender_name = user.full_name
#         if not sender_name and user.first_name and user.last_name:
#             sender_name = f'{user.first_name} {user.last_name}'

#         profile_name = profile.full_name
#         if not profile_name and profile.first_name and profile.last_name:
#             profile_name = f'{profile.first_name} {profile.last_name}'

#         data = {
#             'email': email,
#             'link': link,
#             'sender_name': sender_name,
#             'sender_full_name': user.full_name,
#             'sender_brand_name': user.brand_name,
#             'sender_first_name': user.first_name,
#             'sender_last_name': user.last_name,
#             'sender_middle_name': user.middle_name,
#             'sender_email': user.email,
#             'sender_phone_number': user.phone_number,
#             'sender_avatar': user.avatar,
#             'profile_name': profile_name,
#         }

#         context = Context(data)
#         template = Template(email_template.html)
#         html_content = template.render(context)
#         title = 'You are invited to the following profile at VIO'
#         if settings.USE_SES:
#             container = get_container()
#             aws_ses_services = container.services.aws_ses_service()
#             response, error = aws_ses_services.send_email(
#                 title,
#                 email,
#                 html_content,
#             )
#             EmailLog.objects.create(
#                 email=email,
#                 subject=title,
#                 body=html_content,
#                 response=response,
#                 error=error,
#             )
#         else:
#             send_mail(
#                 title,
#                 '',
#                 settings.EMAIL_HOST_USER,
#                 [email],
#                 html_message=html_content,
#             )


# def create_multiple_users_and_send_cred(
#         users,
#         user_type,
#         profile_template,
#         language,
#         send_confirm,
#         same_password=False,
#         force_send_email=True,
# ):
#     """Send email with credential"""
#     email_subject = 'Welcome to VIO'
#     email_template = None
#     if language == EmailTemplateLanguage.ENG:
#         email_template = EmailTemplate.objects.filter(code='welcome_user_en').first()
#         email_subject = 'Welcome to VIO'
#     elif language == EmailTemplateLanguage.VIE:
#         email_template = EmailTemplate.objects.filter(code='welcome_user_vi').first()
#         email_subject = 'Chào mừng bạn đến với VIO!'

#     profile_template_instance = None
#     if profile_template is not None:
#         profile_template_instance = ProfileTemplate.objects.filter(
#             id=profile_template,
#         ).first()

#     default_password = settings.DEFAULT_USER_PASSWORD
#     bcc_addresses = SystemConfig.objects.get_value(
#         SystemConfigFolder.EMAIL.value,
#         SystemConfigName.BCC_ADDRESSES.value,
#     )
#     if bcc_addresses:
#         bcc_addresses = [bcc_address for bcc_address in bcc_addresses if bcc_address]

#     result = []
#     for user in users:
#         email = user.get('email', '')
#         phone_number = user.get('phone_number', '')

#         if not email and not phone_number:
#             continue
#         try:
#             if phone_number:
#                 phone_number = validate_phone_number(phone_number, country_code=settings.DEFAULT_COUNTRY_CODE)
#         except ValidationError:
#             logger.info('The phone number: %s is not valid. Continue...' % phone_number)
#             phone_number = None
#             if not email:
#                 continue
#         full_name = user.get('full_name')
#         if not full_name:
#             full_name = f"{user.get('last_name')} {user.get('first_name')}"
#         password = default_password if same_password else get_random_string(8)

#         has_created = True
#         instance = None
#         if email and phone_number:
#             """Case 1: existing both email and phone number"""
#             instance = User.objects.filter(
#                 Q(email=email) | Q(phone_number=phone_number),
#             ).first()
#         elif email and not phone_number:
#             """Case 2: existing only email"""
#             instance = User.objects.filter(email=email).first()
#         elif not email and phone_number:
#             """Case 2: existing only phone number"""
#             instance = User.objects.filter(phone_number=phone_number).first()

#         try:
#             if instance is None:
#                 instance = User(
#                     first_name=user.get('first_name'),
#                     last_name=user.get('last_name'),
#                     full_name=full_name,
#                     is_active=True,
#                     profile_type=user_type,
#                     password=make_password(password),
#                 )
#                 if email:
#                     instance.email = email
#                 if phone_number:
#                     instance.phone_number = phone_number

#                 instance.save()
#             else:
#                 if same_password or force_send_email:
#                     instance.password = make_password(password)

#                 instance.is_active = True
#                 instance.save()
#                 has_created = False

#             if user_type == UserTypeOption.PERSONAL and profile_template_instance is not None:
#                 _, created = Participant.objects.get_or_create(
#                     profile_template=profile_template_instance,
#                     user=instance,
#                 )

#             if email and (has_created or force_send_email) and send_confirm:
#                 if email_template is not None:
#                     data = {
#                         'full_name': full_name,
#                         'email': email,
#                         'phone_number': phone_number,
#                         'password': password,
#                     }

#                     context = Context(data)
#                     template = Template(email_template.html)
#                     html_content = template.render(context)
#                     if settings.USE_SES:
#                         container = get_container()
#                         aws_ses_services = container.services.aws_ses_service()
#                         response, error = aws_ses_services.send_email(
#                             email_subject,
#                             email,
#                             html_content,
#                             bcc_addresses=bcc_addresses,
#                         )
#                         EmailLog.objects.create(
#                             email=email,
#                             subject=email_subject,
#                             body=html_content,
#                             bcc_addresses=bcc_addresses,
#                             response=response,
#                             error=error,
#                         )

#                     else:
#                         send_mail(
#                             email_subject,
#                             '',
#                             settings.EMAIL_HOST_USER,
#                             [email],
#                             html_message=html_content,
#                         )

#                 """TODO: Send SMS notice user"""
#                 pass

#         except Exception as e:
#             logger.error(f'Task create_multiple_users_and_send_cred error: '
#                          f'user_type={user_type}, profile_template={profile_template}, email={email}, '
#                          f'phone_number={phone_number}')
#             logger.error(f'Task create_multiple_users_and_send_cred error: {e}')

#         """Should delay this loop process for saving firebase quota"""
#         result.append(instance)
#         time.sleep(5)

#     return result


# def add_user_settings(user_id: int):
#     try:
#         User.objects.get(pk=user_id)
#     except User.DoesNotExist:
#         logger.info(f'The user does not exist. User ID: {user_id}')
#         return None

#     setting_keys = DEFAULT_USER_SETTINGS.keys()
#     user_settings = []
#     for setting_key in setting_keys:
#         try:
#             UserSetting.objects.get(
#                 key=setting_key,
#                 user_id=user_id,
#             )
#         except UserSetting.DoesNotExist:
#             user_setting = UserSetting(
#                 key=setting_key,
#                 data=DEFAULT_USER_SETTINGS[setting_key],
#                 user_id=user_id,
#             )
#             user_settings.append(user_setting)

#     UserSetting.objects.bulk_create(user_settings)


# @app.task
# def deactivate_user_process(user_id: int):
#     user = User.objects.get(id=user_id)
#     logger.info(f'Cancel notify to user = {user.email}; id = {user_id}')
#     now = timezone.now()

#     event_ids = user.events.filter(user_id=user_id,
#                                    start__gte=now,
#                                    status__in=[Event.ONGOING, Event.UPCOMING],
#                                    ).only('id').values_list('id', flat=True)

#     events = Event.objects.filter(id__in=list(event_ids))
#     for event in events:
#         # cancel ongoing and future events
#         event.cancel_events_recurring(is_all_series=event.is_reoccurring)
#         # cancel to receive notify
#         add_task(
#             'events.tasks.send_event_cancelled_notification',
#             event_id=event.id,
#             on_transaction_commit=True,
#         )


# @app.task
# def task_email_tracking_result(result, extra=None):
#     filter_value = {
#         'user': result.get('user'),
#         'template_name': result.get('template_name'),
#         'action': result.get('action'),
#     }
#     if extra and extra.get('code'):
#         filter_value['extra_data__code'] = extra.get('code')

#     tracked, created = EmailTracking.objects.get_or_create(**filter_value)
#     if created:
#         tracked.opened_count = 1
#     else:
#         tracked.opened_count = tracked.opened_count + 1

#     if extra:
#         tracked.extra_data = extra

#     tracked.save()


# def delete_user_social_auth(user_social_auth_id: int, user_id: int, provider: str):
#     try:
#         user_social_auth = UserSocialAuth.objects.get(id=user_social_auth_id)
#     except UserSocialAuth.DoesNotExist:
#         return

#     user_social_auth.delete()

#     batch_size = 50
#     queryset = Event.objects.filter(
#         user_id=user_id,
#         provider=provider,
#     )
#     while True:
#         batch_ids = queryset.values_list('pk')[:batch_size]
#         count = batch_ids.count()
#         if not count:
#             break
#         with transaction.atomic():
#             queryset.filter(pk__in=batch_ids).delete()

#     Event.fix_tree(fix_paths=True)
