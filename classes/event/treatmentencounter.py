from classes.event.encounter import Encounter, EncounterFactory

class TreatmentEncounter(Encounter):
    def __init__(self, patientid, date, days_since_epoch, days_since_relapse, **kwargs):
        super(TreatmentEncounter, self).__init__(patientid, date, "TreatmentEncounter")
        self.days_since_relapse = days_since_relapse
        self.days_since_hct = days_since_epoch
        self.induction_chemo = None
        self.consolidation_chemo = None
        self.hydroxyurea = None
        self.intrathecal_therapy = None
        self.radiation = None
        self.hypomethylating = None
        self.targeted = None
        self.checkpoint_inhibitors = None
        self.cytokine = None
        self.cli = None
        self.hct = None
        self.other_np = None
        self.palliative_chemo = None
        self.other_tcell_targeted = None
        self.set_treatments(**kwargs)

    def set_treatments(self, **kwargs):
        self.induction_chemo = kwargs.get('induction_chemo', None)
        self.consolidation_chemo = kwargs.get('consolidation_chemo', None)
        self.hydroxyurea = kwargs.get('hydroxyurea', None)
        self.intrathecal_therapy = kwargs.get('intrathecal_therapy', None)
        self.radiation = kwargs.get('radiation', None)
        self.hypomethylating = kwargs.get('hypomethylating', None)
        self.targeted = kwargs.get('targeted', None)
        self.checkpoint_inhibitors = kwargs.get('checkpoint_inhibitors', None)
        self.cytokine = kwargs.get('cytokine', None)
        self.cli = kwargs.get('cli', None)
        self.hct = kwargs.get('hct', None)
        self.other_np = kwargs.get('other_np', None)
        self.palliative_chemo = kwargs.get('palliative_chemo', None)
        self.other_tcell_targeted = kwargs.get('other_tcell_targeted', None)

    @property
    def treatments(self):
        return [self.induction_chemo,
                self.consolidation_chemo,
                self.hydroxyurea,
                self.intrathecal_therapy,
                self.radiation,
                self.hypomethylating,
                self.targeted,
                self.checkpoint_inhibitors,
                self.cytokine,
                self.cli,
                self.hct,
                self.other_np,
                self.palliative_chemo,
                self.other_tcell_targeted,
                ]

    def has_consolidation_maintenance(self):
        '''
        whether consolidation/maintenance therapy was administered
        per Krakow JUL19:
            1 : when rx_indication in [3 (Consolidation of CR),4(Maintenance of CR),•	1 : when rx_indication in [3 (Consolidation of CR),4(Maintenance of CR),
            8 (Consolidation f/b “maintenance” (no restaging between))];

            0 Otherwise
        >>> encounter = TreatmentEncounter(date="7-11-2019", patientid=123, days_since_epoch=3, days_since_relapse=2)
        >>> encounter.has_consolidation_maintenance()
        False
        >>> encounter.hydroxyurea = 1
        >>> encounter.has_consolidation_maintenance()
        True
        '''
        return any((self.hydroxyurea, self.intrathecal_therapy, self.checkpoint_inhibitors))

    def is_decision_point(self):
        '''
        return whether the treatment encounter should be considered a decision point
        per Krakow JUL19:
            Including a consolidation or maintenance treatment,
            but not “Hydroxyurea”. Anything on a Treatment Event CRF
            is a decision point except Hydroxyurea.
            …. Not sure whether we should bother with IT therapy, other palliative chemotherapy….
            Maybe exclude IT therapy, Hydroxyurea and other palliative chemotherapy
            as counting as “treatments” of interest.
        :return:
        >>> encounter = TreatmentEncounter(date="7-11-2019", patientid=123, days_since_epoch=3, days_since_relapse=2)
        >>> encounter.is_decision_point()
        False
        >>> encounter.induction_chemo = 0
        >>> encounter.is_decision_point()
        False
        >>> encounter.induction_chemo = 1
        >>> encounter.is_decision_point()
        True
        '''
        return any((self.induction_chemo,
                self.consolidation_chemo,
                self.radiation,
                self.targeted,
                self.checkpoint_inhibitors,
                self.cytokine,
                self.cli,
                self.hct,
                self.other_np,
                self.other_tcell_targeted))

class TreatmentEncounterFactory(EncounterFactory):
    """

    >>> import datetime as dt
    >>> import pandas as pd
    >>> factory = TreatmentEncounterFactory()
    >>> df = pd.DataFrame.from_dict({'date_treatment': [dt.datetime(year=2019, month=7, day=29)],
    ... 'subject_id': [12345],
    ... 'days_hct1_to_tx': [3],
    ... 'days_index_relapse_to_tx': [2],
    ... 'e_treatment__1': [0],
    ... 'e_treatment__2':  [0],
    ... 'e_treatment__3': [0],
    ... 'e_treatment__4': [0],
    ... 'e_treatment__5': [0],
    ... 'e_treatment__6': [0],
    ... 'e_treatment__7': [0],
    ... 'e_treatment__8': [0],
    ... 'e_treatment__9': [0],
    ... 'e_treatment__10': [0],
    ... 'e_treatment__11': [0],
    ... 'e_treatment__12': [0],
    ... 'e_treatment__13': [0],
    ... 'e_treatment__14': [None],
    ...  })
    >>> encounter = factory.make_encounters(df)
    >>> print(encounter)
    [TreatmentEncounter instance: patientid: 12345 date: 2019-07-29 type: TreatmentEncounter]
    """
    def __init__(self):
        super(TreatmentEncounterFactory, self).__init__(TreatmentEncounter)

    def translate_df_to_dict(self, df_row):
        row_dictionary = dict()
        row_dictionary['date'] = df_row['date_treatment']
        row_dictionary['patientid'] = df_row['subject_id']
        row_dictionary['days_since_epoch'] = df_row['days_hct1_to_tx']
        row_dictionary['days_since_relapse'] = df_row['days_index_relapse_to_tx']
        row_dictionary['induction_chemo'] = df_row['e_treatment__1']
        row_dictionary['consolidation_chemo'] = df_row['e_treatment__2']
        row_dictionary['hydroxyurea'] = df_row['e_treatment__3']
        row_dictionary['intrathecal_therapy'] = df_row['e_treatment__4']
        row_dictionary['radiation'] = df_row['e_treatment__5']
        row_dictionary['hypomethylating'] = df_row['e_treatment__6']
        row_dictionary['targeted'] = df_row['e_treatment__7']
        row_dictionary['checkpoint_inhibitors'] = df_row['e_treatment__8']
        row_dictionary['cytokine'] = df_row['e_treatment__9']
        row_dictionary['cli'] = df_row['e_treatment__10']
        row_dictionary['hct'] = df_row['e_treatment__11']
        row_dictionary['other_np'] = df_row['e_treatment__12']
        row_dictionary['palliative_chemo'] = df_row['e_treatment__13']
        row_dictionary['other_tcell_targeted'] = df_row['e_treatment__14']

        return row_dictionary

if __name__ == '__main__':
    import doctest

    doctest.testmod()