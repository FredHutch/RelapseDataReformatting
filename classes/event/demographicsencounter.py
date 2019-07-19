from classes.event.encounter import Encounter

class DemographicsEncounter(Encounter):
    def __init__(self, df_row):
        date = df_row['hct1_date_manual']
        patientid = df_row['uwid']
        date_epoch = df_row['hct1_date_manual']
        date_relapse = df_row['relapse_date_manual']
        super(DemographicsEncounter, self).__init__(patientid, date, "DemographicsEncounter")

    @property
    def codes(self):
        raise NotImplementedError("{c} has not implemented get_codes yet!".format(type(self).__name__))
