import datetime as dt
class Encounter():
    def __init__(self, patientid, date, encountertype):
        self.date = date
        if type(date) is not dt.datetime:
            self.date = dt.datetime.strptime(date, '%m-%d-%Y')
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
        raise NotImplementedError("{c} has not implemented codes yet!".format(c=type(self).__name__))

    @property
    def treatments(self):
        raise NotImplementedError("{c} has not implemented treatments yet!".format(c=type(self).__name__))

    def is_decision_point(self):
        """
        Is this encounter a decision point?
        :return: True if encounter is a valid decision point.
                 False Otherwise
        """
        raise NotImplementedError("{c} has not implemented is_decision_point yet!".format(c=type(self).__name__))


class EncounterFactory:
    def __init__(self, encounterType):
        self.encounterType = encounterType

    def make_encounters(self, events_df):
        events = []
        for row in events_df:
            dict = self.translate_df_to_dict(row)
            events.append(self.encounterType(**dict))

        return events

    def translate_df_to_dict(self, df_row):
        raise NotImplementedError("{c} has not implemented translate_df_to_dict yet!".format(c=type(self).__name__))
