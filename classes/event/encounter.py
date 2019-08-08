import datetime as dt
import pandas as pd
class Encounter():
    def __init__(self, patientid, date, encountertype, **kwargs):
        self.date = date
        if type(date) is pd.Timestamp:
            self.date = date.date()
        elif type(date) is not dt.datetime:
            self.date = dt.datetime.strptime(date, '%m-%d-%Y')
        self.type = encountertype
        self.patientid = patientid
        self.raw_df = kwargs.get("raw_df", None)

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
        """
        return the features for use in creating training rows
        :return:
        >>> import datetime as dt
        >>> import pandas as pd
        >>> raw_df = pd.DataFrame({"pid": 123, "date":dt.datetime.strptime("7-11-2019", '%m-%d-%Y'), "cat":"meow"}, index=[0])
        >>> enc = Encounter(123, dt.datetime.strptime("7-11-2019", '%m-%d-%Y') , "dummy", raw_df=raw_df)
        >>> enc.features
        {'pid': 123, 'date': Timestamp('2019-07-11 00:00:00'), 'cat': 'meow'}
        >>> raw_df = {"pid": 456, "date":dt.datetime.strptime("7-11-2019", '%m-%d-%Y'), "dog":"bork"}
        >>> enc = Encounter(456, dt.datetime.strptime("7-11-2019", '%m-%d-%Y') , "dummy", raw_df=raw_df)
        >>> enc.features
        {'pid': 456, 'date': datetime.datetime(2019, 7, 11, 0, 0), 'dog': 'bork'}
        """
        if type(self.raw_df) == pd.DataFrame:
            return self.raw_df.to_dict(orient='records')[0]
        if type(self.raw_df) == dict:
            return self.raw_df
        if self.raw_df is None:
            return None
        return ValueError(
            "the Dataframe supplied to Encounter {c} is invalid!: {df}".format(c=type(self).__name__, df=self.raw_df))

    @property
    def treatments(self):
        return []

    def is_decision_point(self):
        """
        Is this encounter a decision point?
        :return: True if encounter is a valid decision point.
                 False Otherwise
        """
        raise NotImplementedError("{c} has not implemented is_decision_point yet!".format(c=type(self).__name__))

    def is_target(self):
        """
        Is this encounter a target candidate?
        :return: True if encounter is a valid target.
                 False Otherwise
        """
        raise NotImplementedError("{c} has not implemented is_target yet!".format(c=type(self).__name__))


class EncounterFactory:
    def __init__(self, encountertype):
        self.encounterType = encountertype

    def make_encounters(self, events_df):
        events = []
        for i, row in events_df.iterrows():
            dictionary = self.translate_df_to_dict(row)
            events.append(self.encounterType(**dictionary))

        return events

    def translate_df_to_dict(self, df_row):
        raise NotImplementedError("{c} has not implemented translate_df_to_dict yet!".format(c=type(self).__name__))

    def __store_df_row(self, df_row):
        df_dict = dict()
        df_dict["raw_df"] = df_row

        return df_dict