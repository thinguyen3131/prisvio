from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Reset database'

    def handle(self, *args, **options):
        tables = [
            'events_eventinvite',
            'events_event',
            'events_eventreoccurringcycle',
            'events_eventrepeatingconfig',
            'chats_conversation',
            'posts_post',
            'appointment_exclusiontimeframe',
            'appointment_exclusiondate',
            'appointment_customtimeslotsdate',
            'appointment_timeslotsgroup',
            'appointment_appointment',
            'profiletemplate_participant',
            'profiletemplate_eventgroup',
            'profiletemplate_profiletemplate',
            'users_onetimepassword',
            'users_user',
            'chats_chatprofile',
            'system_userrole',
        ]
        cursor = connection.cursor()
        for table in tables:
            cursor.execute(
                f'truncate table {table} restart identity cascade;',
            )
