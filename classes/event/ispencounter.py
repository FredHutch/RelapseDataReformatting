from classes.event.encounter import Encounter, EncounterFactory


class ISPEncounter(Encounter):
    def __init__(self, patientid, date, days_since_epoch, days_since_relapse, **kwargs):
        super(ISPEncounter, self).__init__(patientid, date, days_since_epoch, days_since_relapse, **kwargs)
        self.e_isp = kwargs.get('e_isp', None)
        self.w_isp_stop = kwargs.get('w_isp_stop', None)

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


class ISPEncounterFactory(EncounterFactory):
    def __init__(self):
        super(ISPEncounterFactory, self).__init__(ISPEncounter)

    def translate_df_to_dict(self, df_row):
        row_dictionary = self._store_df_row(df_row)
        row_dictionary['date'] = df_row.get('date_isp_action', None)
        row_dictionary['patientid'] = df_row.get('subject_id', None)
        row_dictionary['days_since_epoch'] = df_row.get('days_hct1_to_ispact', None)
        row_dictionary['days_since_relapse'] = df_row.get('days_index_rel_to_ispact', None)
        row_dictionary['e_isp'] = df_row.get('e_isp', None)
        row_dictionary['w_isp_stop'] = df_row.get('w_isp_stop', None)

        return row_dictionary
