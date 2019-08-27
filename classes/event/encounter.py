import datetime as dt
import pandas as pd
from math import isnan
import logging

logger = logging.getLogger(__name__)

class Encounter():
    EXPECTED_DATE_STRING_FORMAT = '%Y-%m-%d'
    def __init__(self, patientid, date, days_since_epoch, days_since_relapse, **kwargs):
        self.date = self._date_coercion(date)
        self.days_since_epoch = days_since_epoch
        self.days_since_relapse = days_since_relapse
        self.type = type(self).__name__
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

    @classmethod
    def _date_coercion(cls, check_date):
        if type(check_date) is pd.Timestamp:
            return check_date
        elif type(check_date) is dt.datetime:
            return check_date
        elif type(check_date) is str:
            return dt.datetime.strptime(check_date, cls.EXPECTED_DATE_STRING_FORMAT)
        else:
            error_str = "Warning! a valid check_date must be passed to Encounter! " \
                        "If it is a string it must be formatted like {}:" \
                        " check_date passed: {} of type {}".format(cls.EXPECTED_DATE_STRING_FORMAT, check_date, type(check_date))
            raise ValueError(error_str)

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
        >>> enc = Encounter(123, dt.datetime.strptime("7-11-2019", '%m-%d-%Y') , 0, 0, raw_df=raw_df)
        >>> enc.features
        {'pid': 123, 'date': Timestamp('2019-07-11 00:00:00'), 'cat': 'meow'}
        >>> raw_df = {"pid": 456, "date":dt.datetime.strptime("7-11-2019", '%m-%d-%Y'), "dog":"bork"}
        >>> enc = Encounter(456, dt.datetime.strptime("7-11-2019", '%m-%d-%Y') , 0, 0, raw_df=raw_df)
        >>> enc.features
        {'pid': 456, 'date': datetime.datetime(2019, 7, 11, 0, 0), 'dog': 'bork'}
        """
        if type(self.raw_df) == pd.DataFrame:
            return self.raw_df.to_dict(orient='records')[0]
        if type(self.raw_df) == pd.Series:
            return self.raw_df.to_dict()
        if type(self.raw_df) == dict:
            return self.raw_df
        if self.raw_df is None:
            return dict()
        return ValueError(
            "the Dataframe supplied to Encounter {c} is invalid!: {df}".format(c=type(self).__name__, df=self.raw_df))

    @property
    def existant_features(self):
        """
        return the subset of features that have tangible information for the encounter
        :return:
        """
        return {k:v for k,v in self.features.items() if type(v) in [float, int, not str] and not isnan(v)}

    @property
    def treatments(self):
        return []

    @property
    def indication(self):
        return None

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


class EncounterFactory():
    def __init__(self, encountertype):
        self.encounterType = encountertype

    def make_encounters(self, patientid, events_df):
        events = []
        df_type = type(events_df)
        if df_type == pd.DataFrame:
            for i, row in events_df.iterrows():
                self._add_event_to_events_list(patientid, row, events)
        elif df_type == pd.Series:
            self._add_event_to_events_list(patientid, events_df, events)

        return events

    def _add_event_to_events_list(self, pid, df_row, events_list):
        df_row = self._add_subjectid_to_df(df_row, pid)
        try:
            dictionary = self.translate_df_to_dict(df_row)
            events_list.append(self.encounterType(**dictionary))
        except ValueError as e:
            logger.warning(
                "A value error occurred when adding events to the events list for type: {}  {e}".format(
                    type(self).__name__, e=e))

    def _add_subjectid_to_df(self, df, pid):
        if 'subject_id' not in df.keys():
            df['subject_id'] = pid
        return df

    def translate_df_to_dict(self, df_row):
        raise NotImplementedError("{c} has not implemented translate_df_to_dict yet!".format(c=type(self).__name__))

    def _store_df_row(self, df_row):
        df_dict = dict()
        df_dict["raw_df"] = df_row

        return df_dict