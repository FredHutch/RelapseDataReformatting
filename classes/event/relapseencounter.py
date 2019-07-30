from classes.event.encounter import Encounter, EncounterFactory

class RelapseEncounter(Encounter):
    RELAPSE = 1
    COMPLETE_RESPONSE = 2

    MORPHOLOGIC_PRESENTATION = 1
    MORPHOLOGIC_EXTRAMEDULLARY_PRESENTATION = 2
    MRD_PRESENTATION = 3

    def __init__(self, patientid, date, days_since_epoch, days_since_relapse, **kwargs):
        super(RelapseEncounter, self).__init__(patientid, date, "RelapseEncounter")
        self.days_since_epoch = days_since_epoch
        self.days_since_relapse = days_since_relapse

        self.event_type = kwargs.get('relapse_or_response', None)
        self.relapse_presentation = kwargs.get('relapse_presentation', None)
        self.cr_depth = kwargs.get('cr_depth', None)

    def is_decision_point(self):
        """
        Is this encounter a decision point?
        :return: True if encounter is a valid decision point.
                 False Otherwise
        """
        return False

    def is_relapse(self):
        """
        Did the patient relapse on the date?
        :return: TRUE if event_type is RELAPSE
                 False, otherwise
        """
        return self.event_type == RelapseEncounter.RELAPSE

    def is_response(self):
        """
        Was a treatment response recorded on this date?
        :return: TRUE if event_type is RESPONSE
                 False, otherwise
        """
        return self.event_type == RelapseEncounter.COMPLETE_RESPONSE

    def is_morphologic_relapse(self):
        """

        :return:
        """
        if (self.event_type == RelapseEncounter.RELAPSE and
            (self.relapse_presentation == RelapseEncounter.MORPHOLOGIC_PRESENTATION or
             self.relapse_presentation == RelapseEncounter.MORPHOLOGIC_EXTRAMEDULLARY_PRESENTATION)):
            return True
        return False

    def is_mrd_relapse(self):
        """

        :return:
        """
        if (self.event_type == RelapseEncounter.RELAPSE and
                self.relapse_presentation == RelapseEncounter.MRD_PRESENTATION):
            return True
        return False

    @property
    def treatments(self):
        return list()


class RelapseEncounterFactory(EncounterFactory):
    def __init__(self):
        super(RelapseEncounterFactory, self).__init__(RelapseEncounter)

    def translate_df_to_dict(self, df_row):
        row_dictionary = dict()
        row_dictionary['date'] = df_row['date_response']
        row_dictionary['patientid'] = df_row['subject_id']
        row_dictionary['days_since_epoch'] = df_row['days_hct1_to_e']
        row_dictionary['days_since_relapse'] = df_row['days_index_relapse_to_e']
        row_dictionary['relapse_or_response'] = df_row['e_response']
        row_dictionary['relapse_presentation'] = df_row['w_relapse']
        row_dictionary['cr_depth'] = df_row['w_crdepth']

        return row_dictionary







