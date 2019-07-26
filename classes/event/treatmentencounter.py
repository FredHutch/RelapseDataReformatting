from classes.event.encounter import Encounter, EncounterFactory

class TreatmentEncounter(Encounter):
    def __init__(self, date, patientid, days_since_epoch, days_since_relapse, **kwargs):
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
        self.set_treatments(kwargs)

    def set_treatments(self, **kwargs):
        self.induction_chemo = kwargs['induction_chemo']
        self.consolidation_chemo = kwargs['consolidation_chemo']
        self.hydroxyurea = kwargs['hydroxyurea']
        self.intrathecal_therapy = kwargs['intrathecal_therapy']
        self.radiation = kwargs['radiation']
        self.hypomethylating = kwargs['hypomethylating']
        self.targeted = kwargs['targeted']
        self.checkpoint_inhibitors = kwargs['checkpoint_inhibitors']
        self.cytokine = kwargs['cytokine']
        self.cli = kwargs['cli']
        self.hct = kwargs['hct']
        self.other_np = kwargs['other_np']
        self.palliative_chemo = kwargs['palliative_chemo']
        self.other_tcell_targeted = kwargs['other_tcell_targeted']

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
        '''
        return (self.hydroxyurea or self.intrathecal_therapy or self.checkpoint_inhibitors)

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
    def __init__(self):
        super(TreatmentEncounterFactory, self).__init__(TreatmentEncounter)

    def translate_df_to_dict(self, df_row):
        dict = dict()
        dict['date'] = df_row['date_treatment']
        dict['patientid'] = df_row['subject_id']
        dict['days_since_epoch'] = df_row['days_hct1_to_tx']
        dict['days_since_relapse'] = df_row['days_index_relapse_to_tx']
        dict['induction_chemo'] = df_row['e_treatment__1']
        dict['consolidation_chemo'] = df_row['e_treatment__2']
        dict['hydroxyurea'] = df_row['e_treatment__3']
        dict['intrathecal_therapy'] = df_row['e_treatment__4']
        dict['radiation'] = df_row['e_treatment__5']
        dict['hypomethylating'] = df_row['e_treatment__6']
        dict['targeted'] = df_row['e_treatment__7']
        dict['checkpoint_inhibitors'] = df_row['e_treatment__8']
        dict['cytokine'] = df_row['e_treatment__9']
        dict['cli'] = df_row['e_treatment__10']
        dict['hct'] = df_row['e_treatment__11']
        dict['other_np'] = df_row['e_treatment__12']
        dict['palliative_chemo'] = df_row['e_treatment__13']
        dict['other_tcell_targeted'] = df_row['e_treatment__14']

        return dict