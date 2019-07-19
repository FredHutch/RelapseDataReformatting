from classes.event.encounter import Encounter


class VitalsEncounter(Encounter):
    def __init__(self, df_row):
        date = df_row['date_treatment']
        patientid = df_row['subject_id']
        days_since_epoch = df_row['days_hct1_to_status']
        days_since_relapse = df_row['days_index_rel_to_status']
        super(VitalsEncounter, self).__init__(patientid, date, "VitalsEncounter")

    @property
    def codes(self):
        raise NotImplementedError("{c} has not implemented get_codes yet!".format(type(self).__name__))
