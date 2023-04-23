import json
import random
from datetime import datetime, time
import time as time_p

from disciplines.models import Discipline, Category
from users.models import Grade
from .models import GenerationEvent, Calendar



def generate(request, cause):
    generation_event = GenerationEvent()
    generation_event.initiation_time = datetime.now()
    generation_event.initiator = request.user
    generation_event.cause = cause

    generation_event.start = datetime.now()
    try:
        cal_id = "".join(random.choices("0123456789abcdef", k=5))

        disciplines = Discipline.objects.filter(date__isnull=False).order_by('date', 'time')
        categories = {category.id: category.name for category in Category.objects.all()}
        grades = {grade.id: grade.name for grade in Grade.objects.all()}

        staff_only = disciplines.filter(date_published=False)
        disciplines = disciplines.filter(date_published=True)

        # go through all disciplines and serialize them
        serialized_disciplines = [serialize_discipline(discipline, categories, grades) for discipline in disciplines]
        serialized_staff_only = [serialize_discipline(discipline, categories, grades) for discipline in staff_only]

        serialized_all = serialized_disciplines + serialized_staff_only

        # sort disciplines by date and then by time
        serialized_disciplines.sort(key=lambda discipline: (discipline['date'], discipline['time'] if discipline['time'] else time(0, 0)))
        serialized_staff_only.sort(key=lambda discipline: (discipline['date'], discipline['time'] if discipline['time'] else time(0, 0)))
        serialized_all.sort(key=lambda discipline: (discipline['date'], discipline['time'] if discipline['time'] else time(0, 0)))

        # serialize the calendars into json
        json_serialized_disciplines = serialize_json_calendar(serialized_disciplines, cal_id)
        json_serialized_staff_only = serialize_json_calendar(serialized_staff_only, cal_id, "Neverejné disciplíny")
        json_serialized_all = serialize_json_calendar(serialized_all, cal_id, "Všetky disciplíny")

        # serialize the calendars into ical
        ical_serialized_disciplines = serialize_ical_calendar(serialized_disciplines, cal_id)
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

        generation_event.end = datetime.now()
        generation_event.duration = generation_event.end - generation_event.start
        generation_event.was_successful = True
        generation_event.result = "generated " + cal_id
        generation_event.generated_id = cal_id
        generation_event.save()

    except Exception as e:
        generation_event.end = datetime.now()
        generation_event.duration = generation_event.end - generation_event.start
        generation_event.was_successful = False
        generation_event.result = str(e)
        generation_event.save()
        return


def serialize_discipline(discipline, categories, grades):
    return {
        'id': discipline.id,
        'name': discipline.name,
        'date': discipline.date,
        'time': discipline.time,
        'location': discipline.location,
        'category': categories[discipline.category.id],
        'grades': [grades[grade.id] for grade in discipline.target_grades.all()],
    }


def serialize_json_calendar(disciplines, cal_id, description="Kalendár disciplín"):
    cal = {
        'id': cal_id,
        'name': 'Kalendár OH Gamča 2023',
        'description': description,
        'events': [],
    }
    print(disciplines)

    for d in disciplines:
        d = d.copy()
        d['date'] = d['date'].strftime("%Y-%m-%d")
        d['time'] = d['time'].strftime("%H:%M") if d['time'] is not None else None
        cal['events'].append(d)
    return json.dumps(cal)


def serialize_ical_calendar(disciplines, cal_id, description="Kalendár disciplín"):
    cal = "BEGIN:VCALENDAR\n" \
          "VERSION:2.0\n" \
          "PRODID:-//OHGamca2023//Discipliny//SK\n" \
          "CALSCALE:GREGORIAN\n" \
          "METHOD:PUBLISH\n" \
          "X-WR-CALNAME:Kalendár OH Gamča 2023\n" \
          "X-WR-CALDESC:" + description + "\n" \
          "X-WR-TIMEZONE:Europe/Bratislava\n"

    for discipline in disciplines:
        event = "BEGIN:VEVENT\n" \
                "UID:" + str(discipline['id']) + "\n" \
                "SUMMARY:" + discipline['name'] + "\n"

        if discipline['time'] is not None:
            event += "DTSTAMP:" + discipline['date'].strftime("%Y%m%d") + "T" + discipline['time'].strftime("%H%M%S") + "\n"
        else:
            event += "DTSTAMP:" + discipline['date'].strftime("%Y%m%d") + "T000000\n"

        if discipline['location'] is not None:
            event += "LOCATION:" + discipline['location'] + "\n"

        event += "CLASS:" + discipline['category'] + "\n" \
            "CATEGORIES:" + ",".join(discipline['grades']) + "\n" \
            "END:VEVENT\n"

        cal += event

    cal += "END:VCALENDAR\n"
    return cal