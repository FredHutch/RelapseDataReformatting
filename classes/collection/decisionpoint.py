from classes.collection.eventday import EventDay
from typing import List


class DecisionPoint:
    def __init__(self, eventdays: List[EventDay]):
        self.eventdays = eventdays
        self.eval_date = max(ed.date for ed in eventdays)
        self.treatments = set(ed.treatments for ed in eventdays)
        self.label = None
        self.label_cause = None

    def add_event_day(self, event_day: EventDay):
        self.eventdays.append(event_day)
        self.eval_date = max(self.eval_date, event_day.date)
        self.treatments.update(event_day.treatments)

