from classes.encounter import Encounter

class RelapseEncounter(Encounter):
    def __init__(self, df_row):
        date = df_row['date_response']
        patientid = df_row['subject_id']
        days_since_relapse = df_row['days_index_relapse_to_e']
        days_since_epoch = df_row['days_hct1_to_e']
        super(RelapseEncounter, self).__init__(patientid, date, "RelapseEncounter")
        self.event_type = df_row['e_response']
        self.days_since_relapse = days_since_relapse
        self.days_since_hct = days_since_epoch



