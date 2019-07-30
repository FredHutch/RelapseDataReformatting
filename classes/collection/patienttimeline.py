from typing import List
from classes.collection.eventday import EventDay


class PatientTimeline:
    def __init__(self, eventdays: List[EventDay]):
        self.event_days = eventdays

    def get_sorted_events(self):
        return sorted(self.event_days, lambda x: x.date)

    def get_events_after_date(self, date):
        """
        return list of event days that occur strictly after a given date
        :param date:
        :return: self.event_days with date > param date
        """
        sorted_days = sorted(self.event_days, lambda x: x.date)
        return  [ed for ed in sorted_days if ed.date > date]
