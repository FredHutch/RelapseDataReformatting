import datetime as dt
from classes.event.encounter import Encounter, EncounterFactory


class ISPEncounter(Encounter):
    ISP_STOP_VAR = 2
    def __init__(self, patientid, date, days_since_epoch, days_since_relapse, **kwargs):
        super(ISPEncounter, self).__init__(patientid, date, days_since_epoch, days_since_relapse, **kwargs)
        self.e_isp = kwargs.get('e_isp', None)
        self.isp_event = kwargs.get('isp_event', None)

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

    @property
    def features(self):
        f = super(ISPEncounter, self).features
        f['isp_event'] = self.isp_event
        return f

class ISPEncounterFactory(EncounterFactory):
    def __init__(self):
        super(ISPEncounterFactory, self).__init__(ISPEncounter)
    def translate_df_to_dict(self, df_row):
        row_dictionary = self._store_df_row(df_row)
        row_dictionary['date'] = Encounter._date_coercion(df_row['date_isp_action']) - \
                                dt.timedelta(days=min(0,df_row.get('days_hct1_to_ispact')))
        row_dictionary['days_since_epoch'] = max(0,df_row.get('days_hct1_to_ispact', 0))
        row_dictionary['patientid'] = df_row.get('subject_id', None)
        row_dictionary['days_since_relapse'] = df_row.get('days_index_rel_to_ispact', None)
        row_dictionary['e_isp'] = df_row.get('e_isp', None)
        # do not encode ISP stop dates to look just like start and restart dates
        if row_dictionary['e_isp'] != ISPEncounter.ISP_STOP_VAR:
            row_dictionary['isp_event'] = 1
        return row_dictionary
