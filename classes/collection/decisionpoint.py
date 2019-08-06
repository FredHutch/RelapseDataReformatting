from classes.collection.eventday import EventDay
from typing import List


class DecisionPoint:
    def __init__(self, eventdays: List[EventDay]):
        self.eventdays = eventdays
        if type(eventdays) is EventDay:
            self.eventdays = [eventdays]
        self.label = None
        self.label_cause = None

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