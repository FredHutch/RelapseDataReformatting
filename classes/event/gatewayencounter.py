from classes.event.encounter import Encounter, EncounterFactory


class gatewayEncounter(Encounter):
    def __init__(self, patientid, date, days_since_epoch, days_since_relapse, **kwargs):
        super(gatewayEncounter, self).__init__(patientid, date, "gatewayEncounter")
        self.days_since_epoch = days_since_epoch
        self.days_since_relapse = days_since_relapse
        # to-do: get days_since_epoch and days_since_relapse from PatientTimeline

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


class gatewayEncounterFactory(EncounterFactory):
    def __init__(self):
        super(gatewayEncounterFactory, self).__init__(gatewayEncounter)

    def translate_df_to_dict(self, df_row):
        row_dictionary = self._store_df_row(df_row)
        row_dictionary['date'] = df_row.get('txdate', None)
        row_dictionary['patientid'] = df_row.get('uwid', None)

        return row_dictionary
