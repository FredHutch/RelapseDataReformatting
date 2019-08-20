from classes.collection.eventday import EventDay
from typing import List


class DecisionPoint:
    def __init__(self, patientid, eventdays: List[EventDay]):
        self.patientid = patientid
        self.eventdays = eventdays
        if type(eventdays) is EventDay:
            self.eventdays = [eventdays]
        self.label = None
        self.label_cause = None
        self.target_date = None

    def __eq__(self, other):
        if isinstance(other, DecisionPoint):
            return all([self.patientid == other.patientid, self.eventdays == other.eventdays, self.label == other.label,
                        self.label_cause == other.label_cause])
        return False

    def __repr__(self):
        return "{c} instance: patientid: {pid} eventdays: {ed} label: {l} label_cause: {lc}".format(c=type(self).__name__,
                                                                           pid=self.patientid,
                                                                           ed=self.eventdays,
                                                                           l=self.label,
                                                                           lc=self.label_cause)

    def __str__(self):
        return "patientid: {pid} eventdays: {ed} label: {l} label_cause: {lc}".format(c=type(self).__name__,
                                                                           pid=self.patientid,
                                                                           ed=self.eventdays,
                                                                           l=self.label,
                                                                           lc=self.label_cause)

    def add_event_day(self, event_day: EventDay):
        if type(event_day) is EventDay:
            self.eventdays.append(event_day)
        elif type(event_day) is list:
            for ed in event_day:
                self.eventdays.append(ed)
        else:
            raise ValueError("Cannot add a non-event day to the decision point!")

    @property
    def eval_date(self):
        """
        Return the datetime to be used for decision point evaluation
        """
        return max(ed.date for ed in self.eventdays)

    @property
    def treatments(self):
        """
        Return the datetime to be used for decision point evaluation
        """
        return set(treatment for ed in self.eventdays for treatment in ed.treatments)


if __name__ == '__main__':
    import doctest

    doctest.testmod()