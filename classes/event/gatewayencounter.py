from classes.event.encounter import Encounter, EncounterFactory


class gatewayEncounter(Encounter):
    def __init__(self, patientid, date, days_since_epoch=0, days_since_relapse=0,**kwargs):
        super(gatewayEncounter, self).__init__(patientid, date, days_since_epoch, days_since_relapse, **kwargs)
        
    def is_decision_point(self):
        """
        Is this encounter a decision point?
        :return: True if encounter is a valid decision point.
                 False Otherwise
        """
        return False


class gatewayEncounterFactory(EncounterFactory):
    def __init__(self):
        super(gatewayEncounterFactory, self).__init__(gatewayEncounter)

    def translate_df_to_dict(self, df_row):
        row_dictionary = self._store_df_row(df_row)        
        row_dictionary['date'] = df_row.get('txdate', None)
        row_dictionary['patientid'] = df_row.get('uwid', None) 
        row_dictionary['days_since_epoch'] = 0 #This is hardcoded to be the same day as HCT1
        row_dictionary['days_since_epoch'] = 0
        return row_dictionary
