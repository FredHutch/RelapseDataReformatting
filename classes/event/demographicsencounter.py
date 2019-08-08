from classes.event.encounter import Encounter, EncounterFactory

class DemographicsEncounter(Encounter):
    def __init__(self, patientid, date, days_since_epoch, days_since_relapse, **kwargs):
        super(DemographicsEncounter, self).__init__(patientid, date, "DemographicsEncounter")
        self.days_since_epoch = days_since_epoch
        self.days_since_relapse = days_since_relapse

    def is_decision_point(self):
        """
        Is this encounter a decision point?
        :return: True if encounter is a valid decision point.
                 False Otherwise
        """
        return False


class DemographicsEncounterFactory(EncounterFactory):
    def __init__(self):
        super(DemographicsEncounterFactory, self).__init__(DemographicsEncounter)

    def translate_df_to_dict(self, df_row):
        row_dictionary = self.__store_df_row(df_row)
        row_dictionary['date'] = df_row['hct1_date_manual']
        row_dictionary['patientid'] = df_row['uwid']
        row_dictionary['days_since_epoch'] = df_row['hct1_date_manual']
        row_dictionary['days_since_relapse'] = df_row['relapse_date_manual']

        return row_dictionary