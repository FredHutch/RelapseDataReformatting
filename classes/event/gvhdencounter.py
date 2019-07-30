from classes.event.encounter import Encounter, EncounterFactory

class GVHDEncounter(Encounter):
    def __init__(self, patientid, date, days_since_epoch, days_since_relapse, **kwargs):
        super(GVHDEncounter, self).__init__(patientid, date, "GVHDEncounter")
        self.days_since_epoch = days_since_epoch
        self.days_since_relapse = days_since_relapse

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
        dict = dict()
        dict['date'] = df_row['date_gvhd']
        dict['patientid'] = df_row['subject_id']
        dict['days_since_epoch'] = df_row['days_hct1_gvhd']
        dict['days_since_relapse'] = df_row['days_index_relapse_to_gvhd']
        dict['gvhd_type'] = df_row['e_gvhd']
        dict['acute_gvhd_grade'] = df_row['w_sub_agvh_grade']
        dict['chronic_gvhd_severity'] = df_row['w_sub_cgvh_severity']

        return dict
