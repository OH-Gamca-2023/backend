from django.utils import timezone
from huey import crontab
from huey.contrib import djhuey
from backend.data.models import Setting

from backend.disciplines.models import Discipline


@djhuey.task(retries=2, retry_delay=60, name='Send discord message')
def send_discord_message(message):
    # check if DISCORD_NOTIFICATION_WEBHOOK is set in model Settings
    if not Setting.objects.filter(key='DISCORD_NOTIFICATION_WEBHOOK').exists():
        raise Exception('DISCORD_NOTIFICATION_WEBHOOK is not set in model Settings')

    import requests
    import json

    webhook_url = Setting.objects.get(key='DISCORD_NOTIFICATION_WEBHOOK').value
    data = {
        'content': message
    }
    headers = {
        'Content-Type': 'application/json'
    }
    requests.post(webhook_url, data=json.dumps(data), headers=headers)


@djhuey.periodic_task(crontab(minute='0', hour='5'), name='Send week notification')
def send_7day_notification():
    if not Setting.objects.filter(key='DISCORD_NOTIFICATION_WEBHOOK').exists():
        raise Exception('DISCORD_NOTIFICATION_WEBHOOK is not set in model Settings')

    week_from_now = timezone.now() + timezone.timedelta(days=7)
    disciplines = Discipline.objects.filter(date=week_from_now)

    for discipline in disciplines:
        dc_tags = ""
        for user in discipline.primary_organisers.all():
            dc_tags += f"<@{user.discord_id}> " if user.discord_id else f"@{user.username} "

        message = f"Disciplína {discipline.name} sa koná o týždeň.\n{dc_tags}"
        send_discord_message(message)


@djhuey.periodic_task(crontab(minute='0', hour='5'), name='Send 3 day notification')
def send_3day_notification():
    if not Setting.objects.filter(key='DISCORD_NOTIFICATION_WEBHOOK').exists():
        raise Exception('DISCORD_NOTIFICATION_WEBHOOK is not set in model Settings')

    three_days_from_now = timezone.now() + timezone.timedelta(days=3)
    disciplines = Discipline.objects.filter(date=three_days_from_now)

    for discipline in disciplines:
        dc_tags = ""
        for user in discipline.primary_organisers.all():
            dc_tags += f"<@{user.discord_id}> " if user.discord_id else f"@{user.username} "

        message = f"Disciplína {discipline.name} sa koná o 3 dni.\n{dc_tags}"
        send_discord_message(message)


@djhuey.periodic_task(crontab(minute='0', hour='5'), name='Send 1 day notification')
def send_1day_notification():
    if not Setting.objects.filter(key='DISCORD_NOTIFICATION_WEBHOOK').exists():
        raise Exception('DISCORD_NOTIFICATION_WEBHOOK is not set in model Settings')

    one_day_from_now = timezone.now() + timezone.timedelta(days=1)
    disciplines = Discipline.objects.filter(date=one_day_from_now)

    for discipline in disciplines:
        dc_tags = ""
        for user in discipline.primary_organisers.all():
            dc_tags += f"<@{user.discord_id}> " if user.discord_id else f"@{user.username} "

        message = f"Disciplína {discipline.name} sa koná zajtra.\n{dc_tags}"
        send_discord_message(message)


@djhuey.task(name='Send all notifications')
def send_all_notifications():
    # send notifications for all disciplines that aren't in the past
    disciplines = Discipline.objects.filter(date__gte=timezone.now())
    for discipline in disciplines:
        dc_tags = ""
        for user in discipline.primary_organisers.all():
            dc_tags += f"<@{user.discord_id}> " if user.discord_id else f"@{user.username} "

        message = f"Disciplína {discipline.name} sa koná {discipline.date.strftime('%d.%m.%Y')}.\n{dc_tags}"
        send_discord_message(message)