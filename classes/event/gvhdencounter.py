from classes.event.encounter import Encounter, EncounterFactory

class GVHDEncounter(Encounter):
    def __init__(self, patientid, date, days_since_epoch, days_since_relapse, **kwargs):
        super(GVHDEncounter, self).__init__(patientid, date, days_since_epoch, days_since_relapse, **kwargs)
        self.gvhd_type = kwargs.get('gvhd_type', None)
        self.acute_gvhd_grade = kwargs.get('acute_gvhd_grade', None)
        self.chronic_gvhd_severity = kwargs.get('chronic_gvhd_severity', None)

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


class GVHDEncounterFactory(EncounterFactory):
    def __init__(self):
        super(GVHDEncounterFactory, self).__init__(GVHDEncounter)

    def translate_df_to_dict(self, df_row):
        row_dictionary = self._store_df_row(df_row)
        row_dictionary['date'] = df_row.get('date_gvhd', None)
        row_dictionary['patientid'] = df_row.get('subject_id', None)
        row_dictionary['days_since_epoch'] = df_row.get('days_hct1_gvhd', None)
        row_dictionary['days_since_relapse'] = df_row.get('days_index_rel_to_gvhd', None)
        row_dictionary['gvhd_type'] = df_row.get('e_gvhd', None)
        row_dictionary['acute_gvhd_grade'] = df_row.get('w_sub_agvh_grade', None)
        row_dictionary['chronic_gvhd_severity'] = df_row.get('w_sub_cgvh_severity', None)
        row_dictionary['gvhd_event'] = df_row.get('redcap_repeat_instrument', None)

        return row_dictionary
