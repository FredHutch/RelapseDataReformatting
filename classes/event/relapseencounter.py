from classes.event.encounter import Encounter, EncounterFactory

class RelapseEncounter(Encounter):
    def __init__(self, date, patientid, days_since_epoch, days_since_relapse, **kwargs):
        super(RelapseEncounter, self).__init__(patientid, date, "RelapseEncounter")
        self.days_since_epoch = days_since_epoch
        self.days_since_relapse = days_since_relapse

        self.event_type = kwargs['relapse_or_response']
        self.relapse_presentation = kwargs['relapse_presentation']
        self.cr_depth = kwargs['cr_depth']

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

class RelapseEncounterFactory(EncounterFactory):
    def __init__(self):
        super(RelapseEncounterFactory, self).__init__(RelapseEncounter)

    def translate_df_to_dict(self, df_row):
        dict = dict()
        dict['date'] = df_row['date_response']
        dict['patientid'] = df_row['subject_id']
        dict['days_since_epoch'] = df_row['days_hct1_to_e']
        dict['days_since_relapse'] = df_row['days_index_relapse_to_e']
        dict['relapse_or_response'] = df_row['e_response']
        dict['relapse_presentation'] = df_row['w_relapse']
        dict['cr_depth'] = df_row['w_crdepth']

        return dict







