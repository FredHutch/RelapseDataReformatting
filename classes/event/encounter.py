import datetime as dt
class Encounter():
    def __init__(self, patientid, date, encountertype):
        self.date = date
        if type(date) is not dt.datetime:
            self.date = dt.datetime(date)
        self.type = encountertype
        self.patientid = patientid

    def __lt__(self, other):
        return self.date < other.date

    def __repr__(self):
        return "{c} instance: patientid: {pid} date: {d} type: {t}".format(c=type(self).__name__,
                                                                           pid=self.patientid,
                                                                           d=self.date,
                                                                           t=self.type)

    def __str__(self):
        return "patientid: {pid} date: {d} type: {t}".format(pid=self.patientid, d=self.date, t=self.type)

    @property
    def codes(self):
        raise NotImplementedError("{c} has not implemented get_codes yet!".format(type(self).__name__))

    def is_decision_point(self):
        '''
        Is this encounter a decision point?
        :return: True if encounter is a valid decision point.
                 False Otherwise
        '''
        raise NotImplementedError("{c} has not implemented is_decision_point yet!".format(type(self).__name__))