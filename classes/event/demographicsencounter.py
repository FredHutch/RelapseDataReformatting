from classes.event.encounter import Encounter, EncounterFactory

class DemographicsEncounter(Encounter):
    def __init__(self, patientid, date, days_since_epoch, days_since_relapse, **kwargs):
        super(DemographicsEncounter, self).__init__(patientid, date, days_since_epoch, days_since_relapse, **kwargs)

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
        row_dictionary = self._store_df_row(df_row)
        row_dictionary['date'] = df_row['hct1_date_manual']
        row_dictionary['patientid'] = df_row['uwid']
        row_dictionary['days_since_epoch'] = 0 # This is an arbitrary decision since our demographics are static vars
        row_dictionary['days_since_relapse'] = (Encounter._date_coercion(df_row['hct1_date_manual'])\
                                               - Encounter._date_coercion(df_row['relapse_date_manual'])).days #coerce the raw string-date to a relative int

        return row_dictionary