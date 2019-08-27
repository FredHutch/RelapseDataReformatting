from classes.event.encounter import Encounter, EncounterFactory


class VitalsEncounter(Encounter):
    def __init__(self, patientid, date, days_since_epoch, days_since_relapse, **kwargs):
        super(VitalsEncounter, self).__init__(patientid, date, days_since_epoch, days_since_relapse, **kwargs)
        self.death_status = kwargs.get('death_status', None)
        self.status_at_death = kwargs.get('status_at_death', None)
        self.status_last_alive = kwargs.get('status_last_alive', None)

    def is_decision_point(self):
        return False

    def died(self):
        """
        Did the patient die as of this Vitals Encoutner date?
        :return: True if Dead
                 False otherwise
        >>> encounter = VitalsEncounter(patientid=123, date="2019-07-11", days_since_epoch=3, days_since_relapse=2, death_status=2)
        >>> encounter.died()
        False
        >>> encounter.death_status = None
        >>> encounter.died()
        False
        >>> encounter.death_status = 1
        >>> encounter.died()
        True
        """
        return self.death_status == 1

    @property
    def features(self):
        return list()

    @property
    def treatments(self):
        return list()


class VitalsEncounterFactory(EncounterFactory):
    def __init__(self):
        super(VitalsEncounterFactory, self).__init__(VitalsEncounter)

    def translate_df_to_dict(self, df_row):
        row_dictionary = self._store_df_row(df_row)
        row_dictionary['date'] = df_row['date_status']
        row_dictionary['patientid'] = df_row['subject_id']
        row_dictionary['days_since_epoch'] = df_row['days_hct1_to_status']
        row_dictionary['days_since_relapse'] = df_row['days_index_rel_to_status']
        row_dictionary['death_status'] = df_row['e_status']
        row_dictionary['status_at_death'] = df_row['w_status_dead']
        row_dictionary['status_last_alive'] = df_row['w_status_alive']

        return row_dictionary