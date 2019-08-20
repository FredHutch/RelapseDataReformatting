from classes.event.encounter import Encounter, EncounterFactory

class GraftRejectionEncounter(Encounter):
    def __init__(self, patientid, date, days_since_epoch, days_since_relapse, **kwargs):
        super(GraftRejectionEncounter, self).__init__(patientid, date, "GraftRejectionEncounter")
        self.days_since_epoch = days_since_epoch
        self.days_since_relapse = days_since_relapse

        self.chim3_dnr1 = kwargs.get('chim3_dnr1', None)
        self.chim33_dnr2 = kwargs.get('chim33_dnr2', None)
        self.chim33_dnr3 = kwargs.get('chim33_dnr3', None)
        self.chim3_dnr4 = kwargs.get('chim3_dnr4', None)
        self.chim_mark = kwargs.get('chim_mark', None)

    def is_decision_point(self):
        """
        Is this encounter a decision point?
        :return: True if encounter is a valid decision point.
                 False Otherwise
        """
        return False

    @property
    def treatments(self):
        return list()


class GraftRejectionEncounterFactory(EncounterFactory):
    def __init__(self):
        super(GraftRejectionEncounterrFactory, self).__init__(GraftRejectionEncounterEncounter)

    def translate_df_to_dict(self, df_row):
        row_dictionary = self._store_df_row(df_row)
        row_dictionary['date'] = df_row.get('rej_date', None)
        row_dictionary['patientid'] = df_row.get('subject_id', None)
        row_dictionary['days_since_epoch'] = df_row.get('hct1_to_rej', None)
        row_dictionary['days_since_relapse'] = df_row.get('rel_to_rej', None)
        row_dictionary['chim3_dnr1'] = df_row.get('chim3_dnr1', None)
        row_dictionary['chim33_dnr2'] = df_row.get('chim33_dnr2', None)
        row_dictionary['chim33_dnr3'] = df_row.get('chim33_dnr3', None)
        row_dictionary['chim3_dnr4'] = df_row.get('chim3_dnr4', None)
        row_dictionary['chim_mark'] = df_row.get('chim_mark', None)

        return row_dictionary