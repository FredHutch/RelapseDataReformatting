import datetime
import logging
import pandas as pd
from classes.event.encounter import Encounter, EncounterFactory

logger = logging.getLogger(__name__)

class TreatmentEncounter(Encounter):
    INDUCTION = 1
    MRD_TREATMENT = 2
    CONSOLIDATION_CR = 3
    MAINTENANCE_CR = 4
    OTHER_INDICATION = 9

    def __init__(self, patientid, date, start_date, days_since_epoch, days_since_relapse, **kwargs):
        super(TreatmentEncounter, self).__init__(patientid, date, "TreatmentEncounter", **kwargs)
        self.days_since_relapse = days_since_relapse
        self.start_date = self._date_coercion(start_date)
        self.days_since_hct = days_since_epoch
        self.rx_indication = kwargs.get('rx_indication', None)
        self.treatment_dict = dict()
        self.treatment_dict.setdefault(None)
        self.set_treatments(**kwargs)

    def set_treatments(self, **kwargs):
        if not kwargs:
            kwargs = dict()
        self.treatment_dict['induction_chemo'] = kwargs.get('induction_chemo', None)
        self.treatment_dict['consolidation_chemo'] = kwargs.get('consolidation_chemo', None)
        self.treatment_dict['hydroxyurea'] = kwargs.get('hydroxyurea', None)
        self.treatment_dict['intrathecal_therapy'] = kwargs.get('intrathecal_therapy', None)
        self.treatment_dict['radiation'] = kwargs.get('radiation', None)
        self.treatment_dict['hypomethylating'] = kwargs.get('hypomethylating', None)
        self.treatment_dict['targeted'] = kwargs.get('targeted', None)
        self.treatment_dict['checkpoint_inhibitors'] = kwargs.get('checkpoint_inhibitors', None)
        self.treatment_dict['cytokine'] = kwargs.get('cytokine', None)
        self.treatment_dict['cli'] = kwargs.get('cli', None)
        self.treatment_dict['hct'] = kwargs.get('hct', None)
        self.treatment_dict['other_np'] = kwargs.get('other_np', None)
        self.treatment_dict['palliative_chemo'] = kwargs.get('palliative_chemo', None)
        self.treatment_dict['other_tcell_targeted'] = kwargs.get('other_tcell_targeted', None)

    @property
    def treatments(self):
        return [k for k,v in self.treatment_dict.items() if v == 1]

    def has_consolidation_maintenance(self):
        """
        whether consolidation/maintenance therapy was administered
        per Krakow JUL19:
            1 : when rx_indication in [3 (Consolidation of CR),4(Maintenance of CR),•	1 : when rx_indication in [3 (Consolidation of CR),4(Maintenance of CR),
            8 (Consolidation f/b “maintenance” (no restaging between))];

            0 Otherwise
        per Krakow JUL 30: use rx_indication to determine consolidation or maintenance instead
        >>> encounter = TreatmentEncounter(date="7-11-2019", patientid=123, days_since_epoch=3, days_since_relapse=2)
        >>> encounter.has_consolidation_maintenance()
        False
        >>> encounter.treatment_dict['hydroxyurea'] = 1
        >>> encounter.has_consolidation_maintenance()
        True
        """
        return any((self.treatment_dict['hydroxyurea'], self.treatment_dict['intrathecal_therapy'], self.treatment_dict['checkpoint_inhibitors']))

    def is_decision_point(self):
        """
        return whether the treatment encounter should be considered a decision point
        per Krakow JUL19:
            Including a consolidation or maintenance treatment,
            but not “Hydroxyurea”. Anything on a Treatment Event CRF
            is a decision point except Hydroxyurea.
            …. Not sure whether we should bother with IT therapy, other palliative chemotherapy….
            Maybe exclude IT therapy, Hydroxyurea and other palliative chemotherapy
            as counting as “treatments” of interest.
        per Krakow JUL30:
            an 'Other' rx_indication should not be considered for a decision point
        :return:
        >>> encounter = TreatmentEncounter(date="7-11-2019", patientid=123, days_since_epoch=3, days_since_relapse=2)
        >>> encounter.is_decision_point()
        False
        >>> encounter.treatment_dict['induction_chemo'] = 0
        >>> encounter.is_decision_point()
        False
        >>> encounter.treatment_dict['induction_chemo'] = 1
        >>> encounter.rx_indication = TreatmentEncounter.OTHER_INDICATION
        >>> encounter.is_decision_point()
        False
        >>> encounter.treatment_dict['induction_chemo'] = 1
        >>> encounter.rx_indication = TreatmentEncounter.INDUCTION
        >>> encounter.is_decision_point()
        True
        """
        return (self.date == self.start_date
                and any((self.treatment_dict['induction_chemo'],
                        self.treatment_dict['consolidation_chemo'],
                        self.treatment_dict['radiation'],
                        self.treatment_dict['targeted'],
                        self.treatment_dict['checkpoint_inhibitors'],
                        self.treatment_dict['cytokine'],
                        self.treatment_dict['cli'],
                        self.treatment_dict['hct'],
                        self.treatment_dict['other_np'],
                        self.treatment_dict['other_tcell_targeted']))
               and self.rx_indication != TreatmentEncounter.OTHER_INDICATION)

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
    ... 'e_treatment__14': [None],
    ...  })
    >>> encounter = factory.make_encounters(df)
    >>> print(encounter)
    [TreatmentEncounter instance: patientid: 12345 date: 2019-07-29 type: TreatmentEncounter]
    """
    def __init__(self):
        super(TreatmentEncounterFactory, self).__init__(TreatmentEncounter)

    def _add_event_to_events_list(self, pid, df_row, events_list):
        df_row = self._add_subjectid_to_df(df_row, pid)
        df_row = self._add_start_date_to_df(df_row)
        delta = 1
        if not pd.isna(df_row['w_target_stop']):
            msg = "ALERT! Multi-day treatment event found for PatientId {pid}. " \
                  "Splitting into multiple TreatmentEncounter objects. start: {start} stop: {stop}".format(
                pid=pid, start=df_row['date_treatment'], stop=df_row['w_target_stop'])
            logger.debug(msg)
            end_date = TreatmentEncounter._date_coercion(df_row['w_target_stop'])
            start_date = TreatmentEncounter._date_coercion(df_row['date_treatment'])
            delta += (end_date - start_date).days

        for d in range(delta):
            try:
                df_row['date_treatment'] = TreatmentEncounter._date_coercion(df_row['start_date']) + datetime.timedelta(days=d)
                dictionary = self.translate_df_to_dict(df_row)
                events_list.append(self.encounterType(**dictionary))
            except ValueError as e:
                logger.warning(
                    "A value error occurred when adding events to the events list for type: {}  {e}".format(
                        type(self).__name__, e=e))

    def _add_start_date_to_df(self, df):
        df['start_date'] = df['date_treatment']
        return df

    def translate_df_to_dict(self, df_row):
        row_dictionary = self._store_df_row(df_row)
        # this row is modified to show the modeled date in the case of a multi-day Treatment;
        # the original date_treatment is stored below in start_date
        row_dictionary['date'] = df_row.get('date_treatment', None)
        # this is a synthetic row to split represented date ('date') vs date of treatment begun ('start_date')
        row_dictionary['start_date'] = df_row.get('start_date', None)
        row_dictionary['patientid'] = df_row.get('subject_id', None)
        row_dictionary['days_since_epoch'] = df_row.get('days_hct1_to_tx', None)
        row_dictionary['days_since_relapse'] = df_row.get('days_index_relapse_to_tx', None)
        row_dictionary['rx_indication'] = df_row.get('rx_indication', None)

        #begin treatment types
        row_dictionary['induction_chemo'] = df_row.get('e_treatment___1', None)
        row_dictionary['consolidation_chemo'] = df_row.get('e_treatment___2', None)
        row_dictionary['hydroxyurea'] = df_row.get('e_treatment___3', None)
        row_dictionary['intrathecal_therapy'] = df_row.get('e_treatment___4', None)
        row_dictionary['radiation'] = df_row.get('e_treatment___5', None)
        row_dictionary['hypomethylating'] = df_row.get('e_treatment___6', None)
        row_dictionary['targeted'] = df_row.get('e_treatment___7', None)
        row_dictionary['checkpoint_inhibitors'] = df_row.get('e_treatment___8', None)
        row_dictionary['cytokine'] = df_row.get('e_treatment___9', None)
        row_dictionary['cli'] = df_row.get('e_treatment___10', None)
        row_dictionary['hct'] = df_row.get('e_treatment___11', None)
        row_dictionary['other_np'] = df_row.get('e_treatment___12', None)
        row_dictionary['palliative_chemo'] = df_row.get('e_treatment___13', None)
        row_dictionary['other_tcell_targeted'] = df_row.get('e_treatment___14', None)

        return row_dictionary

if __name__ == '__main__':
    import doctest

    doctest.testmod()