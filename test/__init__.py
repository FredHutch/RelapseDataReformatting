from classes.collection.eventday import EventDay
from classes.collection.patienttimeline import PatientTimeline

from typing import List


def _make_event_day(pid, date, **kwargs):
    ed = EventDay(pid, date)
    events = kwargs.get('event_days', None)
    for event in events:
        ed.add_event(event)
    return ed

def _make_timeline(eds: List[EventDay]):
    timeline = PatientTimeline(eds)

    return timeline