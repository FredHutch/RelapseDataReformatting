import datetime as dt
import pandas as pd
class Encounter():
    def __init__(self, patientid, date, encountertype):
        self.date = date
        if type(date) is pd.Timestamp:
            self.date = date.date()
        elif type(date) is not dt.datetime:
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

    def died(self):
        """
        Did the patient die on the date?
        :return: False, unless overwritten
        """
        return False

    def is_response(self):
        """
        Was a treatment response recorded on this date?
        :return: False, unless overwritten
        """
        return False

    def is_relapse(self):
        """
        Did the patient relapse on the date?
        :return: False, unless overwritten
        """
        return False

    @property
    def features(self):
        raise NotImplementedError("{c} has not implemented features yet!".format(c=type(self).__name__))

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
    def __init__(self, encountertype):
        self.encounterType = encountertype

    def make_encounters(self, events_df):
        events = []
        for i, row in events_df.iterrows():
            dict = self.translate_df_to_dict(row)
            events.append(self.encounterType(**dict))

        return events

    def translate_df_to_dict(self, df_row):
        raise NotImplementedError("{c} has not implemented translate_df_to_dict yet!".format(c=type(self).__name__))
