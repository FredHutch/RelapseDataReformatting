from classes.event.encounter import Encounter

class TreatmentEncounter(Encounter):

    def __init__(self, df_row):
        date = df_row['date_treatment']
        patientid = df_row['subject_id']
        days_since_epoch = df_row['days_hct1_to_tx']
        days_since_relapse = df_row['days_index_relapse_to_tx']
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
        self.set_treatments(df_row)

    def set_treatments(self, df_row):
        self.induction_chemo = df_row['e_treatment__1']
        self.consolidation_chemo = df_row['e_treatment__2']
        self.hydroxyurea = df_row['e_treatment__3']
        self.intrathecal_therapy = df_row['e_treatment__4']
        self.radiation = df_row['e_treatment__5']
        self.hypomethylating = df_row['e_treatment__6']
        self.targeted = df_row['e_treatment__7']
        self.checkpoint_inhibitors = df_row['e_treatment__8']
        self.cytokine = df_row['e_treatment__9']
        self.cli = df_row['e_treatment__10']
        self.hct = df_row['e_treatment__11']
        self.other_np = df_row['e_treatment__12']
        self.palliative_chemo = df_row['e_treatment__13']
        self.other_tcell_targeted = df_row['e_treatment__14']

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
        :return:
        '''
        return (self.induction_chemo,
                self.consolidation_chemo,
                self.hydroxyurea,
                self.intrathecal_therapy,
                self.radiation,
                self.targeted,
                self.checkpoint_inhibitors,
                self.cytokine,
                self.cli,
                self.hct,
                self.other_np,
                self.palliative_chemo,
                self.other_tcell_targeted)
