from classes.event.encounter import Encounter, EncounterFactory


class VitalsEncounter(Encounter):
    def __init__(self, date, patientid, days_since_epoch, days_since_relapse, **kwargs):
        super(VitalsEncounter, self).__init__(patientid, date, "VitalsEncounter")
        self.days_since_epoch = days_since_epoch
        self.days_since_relapse = days_since_relapse

        self.death_status = kwargs['death_status']
        self.status_at_death = kwargs['status_at_death']
        self.status_last_alive = kwargs['status_last_alive']

    def is_decision_point(self):
        return False

    @property
    def codes(self):
        return list()

    @property
    def treatments(self):
        return list()


class VitalsEncounterFactory(EncounterFactory):
    def __init__(self):
        super(VitalsEncounterFactory, self).__init__(VitalsEncounter)

    def translate_df_to_dict(self, df_row):
        dict = dict()
        dict['date'] = df_row['date_status']
        dict['patientid'] = df_row['subject_id']
        dict['days_since_epoch'] = df_row['days_hct1_to_status']
        dict['days_since_relapse'] = df_row['days_index_rel_to_status']
        dict['death_status'] = df_row['e_status']
        dict['status_at_death'] = df_row['w_status_dead']
        dict['status_last_alive'] = df_row['w_status_alive']

        return dict