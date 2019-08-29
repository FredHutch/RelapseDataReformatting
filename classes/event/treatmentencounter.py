import datetime
import logging
import pandas as pd
from classes.event.encounter import Encounter, EncounterFactory

logger = logging.getLogger(__name__)

class TreatmentEncounter(Encounter):
    INDICATION_INDUCTION = 1
    INDICATION_MRD_TREATMENT = 2
    INDICATION_CONSOLIDATION_CR = 3
    INDICATION_MAINTENANCE_CR = 4
    INDICATION_OTHER_INDICATION = 9

    DP_INDICATIONS = {"INDICATION_INDUCTION": INDICATION_INDUCTION,
                      "INDICATION_MRD_TREATMENT": INDICATION_MRD_TREATMENT,
                      "INDICATION_CONSOLIDATION_CR": INDICATION_CONSOLIDATION_CR,
                      "INDICATION_MAINTENANCE_CR": INDICATION_MAINTENANCE_CR
                      }

    def __init__(self, patientid, date, start_date, days_since_epoch, days_since_relapse, **kwargs):
        super(TreatmentEncounter, self).__init__(patientid, date, days_since_epoch, days_since_relapse, **kwargs)
        self.start_date = self._date_coercion(start_date)
        self.rx_indication = kwargs.get('rx_indication', None)
        self.treatment_dict = dict()
        self.set_treatments(**kwargs)

    def __repr__(self):
        base = super(TreatmentEncounter, self).__repr__()
        treatment_str = "rx_indication: {ind} treatments: {td}".format(ind=self.rx_indication, td=self.treatment_dict)
        return " ".join([base, treatment_str])

    def __str__(self):
        base = super(TreatmentEncounter, self).__str__()
        treatment_str = "rx_indication: {ind} treatments: {td}".format(ind=self.rx_indication, td=self.treatment_dict)
        return " ".join([base, treatment_str])

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

    @property
    def indication(self):
        return self.rx_indication

    def has_consolidation_maintenance(self):
        """
        whether consolidation/maintenance therapy was administered
        per Krakow JUL19:
            1 : when rx_indication in [3 (Consolidation of CR),4(Maintenance of CR),•	1 : when rx_indication in [3 (Consolidation of CR),4(Maintenance of CR),
            8 (Consolidation f/b “maintenance” (no restaging between))];

            0 Otherwise
        per Krakow JUL 30: use rx_indication to determine consolidation or maintenance instead
        >>> encounter = TreatmentEncounter(date="2019-07-11", start_date="2019-07-11", patientid=123, days_since_epoch=3, days_since_relapse=2)
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
        >>> encounter = TreatmentEncounter(date="2019-07-11", start_date="2019-07-11", patientid=123, days_since_epoch=3, days_since_relapse=2)
        >>> encounter.is_decision_point()
        False
        >>> encounter.treatment_dict['induction_chemo'] = 0
        >>> encounter.is_decision_point()
        False
        >>> encounter.treatment_dict['induction_chemo'] = 1
        >>> encounter.rx_indication = TreatmentEncounter.INDICATION_OTHER_INDICATION
        >>> encounter.is_decision_point()
        False
        >>> encounter.treatment_dict['induction_chemo'] = 1
        >>> encounter.rx_indication = TreatmentEncounter.INDICATION_INDUCTION
        >>> encounter.is_decision_point()
        True
        """

        if self.date == self.start_date:
            if any((self.treatment_dict['induction_chemo'],
                    self.treatment_dict['consolidation_chemo'],
                    self.treatment_dict['radiation'],
                    self.treatment_dict['targeted'],
                    self.treatment_dict['checkpoint_inhibitors'],
                    self.treatment_dict['cytokine'],
                    self.treatment_dict['cli'],
                    self.treatment_dict['hct'],
                    self.treatment_dict['other_np'],
                    self.treatment_dict['other_tcell_targeted']
            )):
                if self.rx_indication != TreatmentEncounter.INDICATION_OTHER_INDICATION:
                    return True

                msg = "TreatmentEncounter NOT DecisionPoint for PatientId: {pid}. Failed at Indication check: " \
                      "Expected Indication: {exp_ind} Actual Indication: {act_ind} Treatments given: {treat} ".format(
                    pid=self.patientid,
                    exp_ind=TreatmentEncounter.DP_INDICATIONS,
                    act_ind=self.rx_indication,
                    treat=self.treatments)
                logger.warning(msg)
                return False
            msg = "TreatmentEncounter NOT DecisionPoint for PatientId: {pid}. Failed at Treatments Given check: " \
                  "Expected Indication: {exp_ind} Actual Indication: {act_ind} Treatments given: {treat} ".format(
                    pid=self.patientid,
                    exp_ind=TreatmentEncounter.DP_INDICATIONS,
                    act_ind=self.rx_indication,
                    treat=self.treatments)
            logger.warning(msg)
            return False
        msg = "TreatmentEncounter NOT DecisionPoint for PatientId: {pid}. Failed at Dates Given check: " \
              "Expected Date: {exp_date} Actual Date: {act_date} " \
              "Expected Indication: {exp_ind} Actual Indication: {act_ind} Treatments given: {treat} ".format(
                pid=self.patientid,
                exp_date=self.start_date,
                act_date=self.date,
                exp_ind=TreatmentEncounter.DP_INDICATIONS,
                act_ind=self.rx_indication,
                treat=self.treatments)
        logger.debug(msg)
        return False


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
    ... 'e_treatment__2': [0],
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
    >>> encounter = factory.make_encounters(patientid=12345, events_df=df)
    >>> print(encounter)
    [TreatmentEncounter instance: patientid: 12345 date: 2019-07-29 00:00:00 type: TreatmentEncounter rx_indication: None treatments: {'induction_chemo': None, 'consolidation_chemo': None, 'hydroxyurea': None, 'intrathecal_therapy': None, 'radiation': None, 'hypomethylating': None, 'targeted': None, 'checkpoint_inhibitors': None, 'cytokine': None, 'cli': None, 'hct': None, 'other_np': None, 'palliative_chemo': None, 'other_tcell_targeted': None}]
    """
    def __init__(self):
        super(TreatmentEncounterFactory, self).__init__(TreatmentEncounter)

    def _add_event_to_events_list(self, pid, df_row, events_list):
        df_row = self._add_subjectid_to_df(df_row, pid)
        df_row = self._add_start_date_to_df(df_row)
        delta = 1
        if not pd.isna(df_row.get('w_target_stop', None)):
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
        if type(df['date_treatment']) is pd.Timestamp:
            df['start_date'] = pd.to_datetime(df['start_date'])
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