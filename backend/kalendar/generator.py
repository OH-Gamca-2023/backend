import json
import random
import time as time_p
import traceback
from datetime import time

from django.utils import timezone

from backend.disciplines.models import Discipline, Category
from backend.users.models import Grade
from .models import GenerationEvent, Calendar, Event


def generate(request, cause):
    generation_event = GenerationEvent()
    generation_event.initiation_time = timezone.now()
    generation_event.initiator = request.user
    generation_event.cause = cause

    generation_event.start = timezone.now()
    try:
        cal_id = "".join(random.choices("0123456789abcdef", k=8))

        disciplines = Discipline.objects.filter(date__isnull=False).order_by('date', 'start_time')
        events = Event.objects.all()
        categories = {category.id: category.name for category in Category.objects.all()}
        grades = {grade.id: grade.name for grade in Grade.objects.all()}

        staff_only = disciplines.filter(date_published=False)
        staff_only_events = events.filter(only_staff=True)
        disciplines = disciplines.filter(date_published=True)
        events = events.filter(only_staff=False)

        # go through all disciplines and serialize them
        serialized = [serialize_discipline(discipline, categories, grades) for discipline in disciplines]
        serialized += [serialize_event(event) for event in events]
        serialized_staff_only = [serialize_discipline(discipline, categories, grades) for discipline in staff_only]
        serialized_staff_only += [serialize_event(event) for event in staff_only_events]

        serialized_all = serialized + serialized_staff_only

        # sort disciplines by date and then by time
        serialized.sort(key=lambda event: (
            event['start_date'], event['start_time'] if event['start_time'] else time(0, 0)))
        serialized_staff_only.sort(key=lambda event: (
            event['start_date'], event['start_time'] if event['start_time'] else time(0, 0)))
        serialized_all.sort(key=lambda event: (
            event['start_date'], event['start_time'] if event['start_time'] else time(0, 0)))

        # serialize the calendars into json
        json_serialized_disciplines = serialize_json_calendar(serialized, cal_id)
        json_serialized_staff_only = serialize_json_calendar(serialized_staff_only, cal_id, "Neverejné disciplíny")
        json_serialized_all = serialize_json_calendar(serialized_all, cal_id, "Všetky disciplíny")

        # serialize the calendars into ical
        ical_serialized_disciplines = serialize_ical_calendar(serialized, cal_id)
        ical_serialized_staff_only = serialize_ical_calendar(serialized_staff_only, cal_id, "Neverejné disciplíny")
        ical_serialized_all = serialize_ical_calendar(serialized_all, cal_id, "Všetky disciplíny")

        # save the calendars
        Calendar.objects.update_or_create(
            key="disciplines_json",
            defaults={
                "content_type": "application/json",
                "content": json_serialized_disciplines,
                "is_current": True,
                "id": cal_id
            }
        )
        Calendar.objects.update_or_create(
            key="staff_only_json",
            defaults={
                "content_type": "application/json",
                "content": json_serialized_staff_only,
                "is_current": True,
                "id": cal_id
            }
        )
        Calendar.objects.update_or_create(
            key="all_json",
            defaults={
                "content_type": "application/json",
                "content": json_serialized_all,
                "is_current": True,
                "id": cal_id
            }
        )
        Calendar.objects.update_or_create(
            key="disciplines_ical",
            defaults={
                "content_type": "text/calendar",
                "content": ical_serialized_disciplines,
                "is_current": True,
                "id": cal_id
            }
        )
        Calendar.objects.update_or_create(
            key="staff_only_ical",
            defaults={
                "content_type": "text/calendar",
                "content": ical_serialized_staff_only,
                "is_current": True,
                "id": cal_id
            }
        )
        Calendar.objects.update_or_create(
            key="all_ical",
            defaults={
                "content_type": "text/calendar",
                "content": ical_serialized_all,
                "is_current": True,
                "id": cal_id
            }
        )
        Calendar.objects.update_or_create(
            key="current",
            defaults={
                "content_type": "text/plain",
                "content": time_p.time(),
                "is_current": True,
                "id": cal_id
            }
        )

        generation_event.end = timezone.now()
        generation_event.duration = generation_event.end - generation_event.start
        generation_event.was_successful = True
        generation_event.result = "generated " + cal_id
        generation_event.generated_id = cal_id
        generation_event.save()

    except Exception:
        generation_event.end = timezone.now()
        generation_event.duration = generation_event.end - generation_event.start
        generation_event.was_successful = False
        generation_event.result = traceback.format_exc()
        generation_event.save()
        return


def serialize_discipline(discipline, categories, grades):
    return {
        'id': discipline.id,
        'name': {
            'regular': discipline.name,
            'short': discipline.short_name if discipline.short_name else discipline.name,
        },
        'date': discipline.date,
        'start_time': discipline.start_time,
        'end_time': discipline.end_time,
        'location': discipline.location,
        'category': {
            'id': discipline.category.id,
            'name': discipline.category.name,
        },
        'grades': [grades[grade.id] for grade in discipline.target_grades.all()],
    }


def serialize_event(event):
    return {
        'id': event.id,
        'name': {
            'regular': event.name,
            'short': event.name,  # Events don't have short name
        },
        'date': event.date,
        'start_time': event.start_time,
        'end_time': event.end_time,
        'location': event.location,
        'category': {
            'id': event.category.id,
            'name': event.category.name,
        },
        'grades': [],  # Events don't have grades
    }


def serialize_json_calendar(disciplines, cal_id, description="Kalendár disciplín"):
    cal = {
        'id': cal_id,
        'name': 'Kalendár OH Gamča 2023',
        'description': description,
        'events': [],
    }

    for d in disciplines:
        d = d.copy()
        d['date'] = d['date'].strftime("%Y-%m-%d")
        d['start_date'] = d['date'].strftime("%Y-%m-%d")  # Compatibility with old format, TODO: remove
        d['start_time'] = d['start_time'].strftime("%H:%M") if d['start_time'] is not None else None
        d['end_time'] = d['end_time'].strftime("%H:%M") if d['end_time'] is not None else None
        d['category'] = d['category']['id']
        cal['events'].append(d)
    return json.dumps(cal)


def serialize_ical_calendar(events, cal_id, description="Kalendár disciplín"):
    cal = "BEGIN:VCALENDAR\n" \
          "VERSION:2.0\n" \
          "PRODID:-//OHGamca2023//Kalendar//SK\n" \
          "CALSCALE:GREGORIAN\n" \
          "METHOD:PUBLISH\n" \
          "X-WR-CALNAME:Kalendár OH Gamča 2023\n" \
          "X-WR-CALDESC:" + description + "\n" \
                                          "X-WR-TIMEZONE:Europe/Bratislava\n"

    for event in events:
        ical_event = "BEGIN:VEVENT\n" \
                     "UID:" + str(event['id']) + "\n" \
                     "SUMMARY:" + event['name']['regular'] + "\n" \
                     "DTSTAMP:" + timezone.now().strftime("%Y%m%dT%H%M%S") + "\n"

        if event['start_time'] is not None:
            ical_event += "DTSTART:" + event['date'].strftime("%Y%m%d") + "T" + event['start_time'].strftime(
                "%H%M%S") + "\n"
            if event['end_time'] is not None:
                ical_event += "DTEND:" + event['date'].strftime("%Y%m%d") + "T" + event['end_time'].strftime(
                    "%H%M%S") + "\n"
        else:
            ical_event += "DTSTART:" + event['date'].strftime("%Y%m%d") + "T000000\n"

        if event['location'] is not None:
            ical_event += "LOCATION:" + event['location'] + "\n"

        ical_event += "CLASS:" + event['category']['name'] + "\n"
        if len(event['grades']) > 0:
            ical_event += "CATEGORIES:" + ",".join(event['grades']) + "\n"
        ical_event += "END:VEVENT\n"

        cal += ical_event

    cal += "END:VCALENDAR\n"
    return cal
