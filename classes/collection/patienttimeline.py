import logging
from typing import List
from datetime import datetime
from classes.collection.eventday import EventDay
from classes.collection.decisionpoint import DecisionPoint

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class PatientTimeline:
    def __init__(self, patientid, eventdays: List[EventDay]):
        self.patientid = patientid
        self.event_days = eventdays
        self.decision_points = list()

    def add_decision_point(self, dp: DecisionPoint):
        if dp.patientid == self.patientid:
            self.decision_points.append(dp)
        else:
            logger.warning(
                "Tried to attach decision point with id: {other} to timeline for: {us}".format(other=dp.patientid,
                                                                                               us=self.patientid))

    def get_sorted_events(self):
        return sorted(self.event_days, key=lambda x: x.date)

    def get_events_after_date(self, date: datetime):
        """
        return list of event days that occur on or after a given date
        :param date:
        :return: self.event_days with date > param date
        """
        sorted_days = sorted(self.event_days, key=lambda x: x.date)
        return  [ed for ed in sorted_days if ed.date > date]

    def get_events_in_range(self, beginningdate: datetime, enddate: datetime):
        """
        return list of event days that occur on or after a given date and strictly before another date
        :param beginningdate: a datetime date
        :param enddate: a datetime date
        :return: self.event_days with date > param date
        """
        sorted_days = sorted(self.event_days, key=lambda x: x.date)
        return [ed for ed in sorted_days if ed.date > beginningdate and ed.date <= enddate]
