import itertools

class EventDay():
    def __init__(self, patientid, date, *events):
        self.date = date
        self.patientid = patientid
        self.events = []
        for event in events:
            self.add_event(event)

    def add_event(self, event):
        """
        Add a new Event to the collection of events for the EventDay's given date and patient

        Fails if either the event date or event patientid do not match the Event_Days
        :param event: Any Encounter object
        :return:
        >>> from datetime import datetime
        >>> from classes.event.encounter import Encounter
        >>> pid = 12345
        >>> dt = datetime.now()
        >>> ed = EventDay(pid, dt)
        >>> e1 = Encounter(pid, dt, "Dummy")
        >>> ed.add_event(e1)
        >>> ed.events[0] == e1
        True
        >>> e2 = Encounter(pid+1, dt, "Dummy")
        >>> ed.add_event(e2)
        Traceback (most recent call last):
            ...
        ValueError: An Error occurred adding an event with patientid 12346 cannot be added to the EventDay collection with patientid 12345
        """

        if event.date != self.date:
            error_msg = "An Error occurred adding an event with date {new_d} cannot be added to the " \
                        "EventDay collection with date {old_d}".format(new_d=event.date, old_d=self.date)
            raise ValueError(error_msg)
        if event.patientid != self.patientid:
            error_msg = "An Error occurred adding an event with patientid {new_pid} cannot be added to the " \
                        "EventDay collection with patientid {old_pid}".format(new_pid=event.patientid,
                                                                              old_pid=self.patientid)
            raise ValueError(error_msg)

        self.events.append(event)

    def is_decision_point(self):
        return any(e.is_decision_point() for e in self.events)

    def died(self):
        return any(e.died() for e in self.events)

    def relapse(self):
        return any(e.is_relapse() for e in self.events)

    def response(self):
        return any(e.is_response() for e in self.events)

    def morphological_relapse(self):
        """
        Add a new Event to the collection of events for the EventDay's given date and patient

        Fails if either the event date or event patientid do not match the Event_Days
        :param event: Any Encounter object
        :return:
        >>> from datetime import datetime
        >>> from classes.event.encounter import Encounter
        >>> from classes.event.relapseencounter import RelapseEncounter
        >>> pid = 12345
        >>> dt = datetime.now()
        >>> ed = EventDay(pid, dt)
        >>> e1 = Encounter(pid, dt, "Dummy")
        >>> ed.add_event(e1)
        >>> ed.morphological_relapse()
        False
        >>> e2 = RelapseEncounter(pid, dt, 3, 1, relapse_or_response=1)
        >>> ed.add_event(e2)
        >>> ed.morphological_relapse()
        False
        >>> e3 = RelapseEncounter(pid, dt, 3, 1, relapse_or_response=1, relapse_presentation=1)
        >>> ed.add_event(e3)
        >>> ed.morphological_relapse()
        True
        """
        return any(e.is_relapse() and e.is_morphologic_relapse() for e in self.events)

    def mrd_relapse(self):
        """
        Add a new Event to the collection of events for the EventDay's given date and patient

        Fails if either the event date or event patientid do not match the Event_Days
        :param event: Any Encounter object
        :return:
        >>> from datetime import datetime
        >>> from classes.event.encounter import Encounter
        >>> from classes.event.relapseencounter import RelapseEncounter
        >>> pid = 12345
        >>> dt = datetime.now()
        >>> ed = EventDay(pid, dt)
        >>> e1 = Encounter(pid, dt, "Dummy")
        >>> ed.add_event(e1)
        >>> ed.mrd_relapse()
        False
        >>> e2 = RelapseEncounter(pid, dt, 3, 1, relapse_or_response=1, relapse_presentation=1)
        >>> ed.add_event(e2)
        >>> ed.mrd_relapse()
        False
        >>> e3 = RelapseEncounter(pid, dt, 3, 1, relapse_or_response=1, relapse_presentation=3)
        >>> ed.add_event(e3)
        >>> ed.mrd_relapse()
        True
        """
        return any(e.is_relapse() and e.is_mrd_relapse() for e in self.events)


    @property
    def features(self):
        return sorted(list(itertools.chain(*[e.features for e in self.events])))

    @property
    def treatments(self):
        return sorted(list(itertools.chain(*[e.treatments for e in self.events])))



if __name__ == "__main__":
    import doctest
    doctest.testmod()