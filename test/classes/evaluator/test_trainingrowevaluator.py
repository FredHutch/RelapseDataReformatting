import datetime as dt
import nose
from nose import with_setup
from nose.tools import assert_equals, assert_in, assert_raises

from classes.collection.decisionpoint import DecisionPoint
from datetime import datetime, timedelta
from classes.event.encounter import Encounter
from classes.collection.eventday import EventDay
from classes.event.relapseencounter import RelapseEncounter
from classes.event.treatmentencounter import TreatmentEncounter
from classes.event.demographicsencounter import DemographicsEncounter
from classes.event.vitalsencounter import VitalsEncounter
from scripts.map_categorical_features import DataDictionary
import classes.evaluator.trainingrowevaluator as tre

from test import _make_event_day, _make_timeline


class TestTrainingRowEvaluator:
    def setup(self):
        self.PID = 12345
        self.EVENT_DATE_ONE = datetime.strptime("7-11-2019", '%m-%d-%Y')
        self.EVENT_START_DATE_ONE = datetime.strptime("7-11-2019", '%m-%d-%Y')
        self.TIME_WINDOW = 5
        self.LONG_TIME_WINDOW = 100
        self.DPOINT_WINDOW = 50
        self.INDEX_EPOCH = 1
        self.INDEX_RELAPSE = 2

        raw_df1 = {'subject_id': self.PID, 'e_treatment___2': 1, 'e_treatment___3': 1}
        raw_df2 = {'subject_id': self.PID, 'e_treatment___2': 1, 'e_treatment___3': 1, 'e_treatment___9': 1}
        raw_df3 = {'subject_id': self.PID, 'relapse_or_response': 1, 'relapse_presentation': 1,}
        raw_df4 = {'subject_id': self.PID, 'e_treatment___9': 1, 'rx_indication': 2}
        raw_df5 = {'subject_id': self.PID, 'relapse_or_response': 1, 'relapse_presentation': 3, }
        raw_df6 = {'subject_id': self.PID, 'e_treatment___2': 1, 'e_treatment___3': 1, 'e_treatment___9': 1, 'rx_indication': 2}
        raw_df7 = {'subject_id': self.PID}

        raw_dfs = {'e1':raw_df1,
                   'e2':raw_df1,
                   'e3':raw_df2,
                   'e4': raw_df3,
                   'e5': raw_df3,
                   'e6': raw_df4,
                   'e7': raw_df5,
                   'e8': raw_df6,
                   'e9': raw_df7,
                   }

        e1 = self._make_encounter_with_timeshift(DemographicsEncounter, self.PID, self.EVENT_DATE_ONE,
                                                            self.INDEX_EPOCH,
                                                            self.INDEX_RELAPSE, hydroxyurea=1, consolidation_chemo=1,
                                                            raw_df=raw_dfs['e1'])
        e2 = self._make_treatment_encounter_with_timeshift(TreatmentEncounter, self.PID, self.EVENT_DATE_ONE, self.EVENT_START_DATE_ONE,
                                                            self.INDEX_EPOCH,
                                                            self.INDEX_RELAPSE, hydroxyurea=1, consolidation_chemo=1,
                                                            raw_df=raw_dfs['e2'])
        e3 = self._make_treatment_encounter_with_timeshift(TreatmentEncounter, self.PID, self.EVENT_DATE_ONE, self.EVENT_START_DATE_ONE,
                                                            self.INDEX_EPOCH,
                                                            self.INDEX_RELAPSE, 2, hydroxyurea=1, cytokine=1,
                                                            consolidation_chemo=1,
                                                            raw_df=raw_dfs['e3'])
        e4 = self._make_encounter_with_timeshift(RelapseEncounter, self.PID, self.EVENT_DATE_ONE,
                                                            self.INDEX_EPOCH,
                                                            self.INDEX_RELAPSE, 3, relapse_or_response=1,
                                                            relapse_presentation=1,
                                                            raw_df=raw_dfs['e4'])
        e5 = self._make_encounter_with_timeshift(RelapseEncounter, self.PID, self.EVENT_DATE_ONE,
                                                            self.INDEX_EPOCH,
                                                            self.INDEX_RELAPSE, 4, relapse_or_response=1,
                                                            relapse_presentation=1,
                                                            raw_df=raw_dfs['e5'])
        e6 = self._make_treatment_encounter_with_timeshift(TreatmentEncounter, self.PID, self.EVENT_DATE_ONE, self.EVENT_START_DATE_ONE,
                                                            self.INDEX_EPOCH,
                                                            self.INDEX_RELAPSE,  5, cytokine=1,
                                                            rx_indication=TreatmentEncounter.INDICATION_MRD_TREATMENT,
                                                            raw_df=raw_dfs['e6'])
        e7 = self._make_encounter_with_timeshift(RelapseEncounter, self.PID, self.EVENT_DATE_ONE,
                                                            self.INDEX_EPOCH,
                                                            self.INDEX_RELAPSE, 6, relapse_or_response=1,
                                                            relapse_presentation=3,
                                                            raw_df=raw_dfs['e7'])
        e8 = self._make_treatment_encounter_with_timeshift(TreatmentEncounter, self.PID, self.EVENT_DATE_ONE,
                                                            self.EVENT_START_DATE_ONE,
                                                            self.INDEX_EPOCH,
                                                            self.INDEX_RELAPSE,  6, cytokine=1, hypomethylating=1,
                                                            rx_indication=TreatmentEncounter.INDICATION_MRD_TREATMENT,
                                                            raw_df=raw_dfs['e8'])
        e9 = self._make_encounter_with_timeshift(VitalsEncounter, self.PID, self.EVENT_DATE_ONE,
                                                            self.INDEX_EPOCH,
                                                            self.INDEX_RELAPSE, 105,
                                                            raw_df=raw_dfs['e9'])


        self.ed1 = _make_event_day(self.PID, self.EVENT_DATE_ONE, event_days=[e1, e2])
        self.ed2 = _make_event_day(self.PID, self.EVENT_DATE_ONE + timedelta(days=2), event_days=[e3])
        self.ed3 = _make_event_day(self.PID, self.EVENT_DATE_ONE + timedelta(days=3), event_days=[e4])
        self.ed4 = _make_event_day(self.PID, self.EVENT_DATE_ONE + timedelta(days=4), event_days=[e5])
        self.ed5 = _make_event_day(self.PID, self.EVENT_DATE_ONE + timedelta(days=5), event_days=[e6])
        self.ed6 = _make_event_day(self.PID, self.EVENT_DATE_ONE + timedelta(days=6), event_days=[e7, e8])
        self.ed7 = _make_event_day(self.PID, self.EVENT_DATE_ONE + timedelta(days=105), event_days=[e9])


        self.evaluator = tre.TrainingRowEvaluator()
        self.timeline = _make_timeline(self.PID, [self.ed1, self.ed2, self.ed3, self.ed4, self.ed5, self.ed6, self.ed7])
        self.datadict = self._make_data_dict()

    def _make_encounter_with_timeshift(self, enc, pid, date, epoch, relapse, offset=0, **kwargs):
        return enc(pid, date + timedelta(days=offset), epoch + offset, relapse + offset, **kwargs)

    def _make_treatment_encounter_with_timeshift(self, enc, pid, date, start_date, epoch, relapse, offset=0, **kwargs):
        return enc(pid, date + timedelta(days=offset), start_date + timedelta(days=offset), epoch + offset,
                   relapse + offset, **kwargs)

    def _make_data_dict(self):
        dd = DataDictionary()
        dd.code_cols = { 'e_treatment___2': ('Code', 'Binary', 'Time-Varying', 'Yes'),
                         'e_treatment___3': ('Code', 'Binary', 'Time-Varying', 'Yes'),
                         'e_treatment___9': ('Code', 'Binary', 'Time-Varying', 'Yes'),
                         }

        dd.code_mappings = {'w_mrd_type___1': 1,
                            'e_treatment___2': 2,
                            'e_treatment___3': 3,
                            'e_treatment___9': 4,
                            'rx_indication___2': 5,
                            'rx_indication___3': 6,
                            }

        dd.drop_cols = ['subject_id']
        dd.numeric_cols = ['relapse_or_response',
                           'relapse_presentation']

        return dd

    def test_evaluate_timeline_for_training_rows_no_decision_points(self):
       with assert_raises(AttributeError) as e:
           self.evaluator.evaluate_timeline_for_training_rows(self.timeline, self.datadict)

    def test_evaluate_timeline_for_training_rows(self):
        dpt1 = DecisionPoint(patientid=self.PID, eventdays=[self.ed1, self.ed2])
        dpt1.label_cause = 'Morphological Relapse'
        dpt1.label = True
        dpt2 = DecisionPoint(patientid=self.PID, eventdays=[self.ed5])
        dpt2.label_cause = "Induction/MRD Indication + New Tx"
        dpt2.label = True
        dpt3 = DecisionPoint(patientid=self.PID, eventdays=[self.ed6])
        dpt3.label_cause = None
        dpt3.label = False
        self.timeline.decision_points = [dpt1, dpt2, dpt3]

        expected = [{'PID': 12345, 'numerics': [[None, None], [None, None]], 'codes': [[2, 3], [2, 3, 4]], 'to_event': [1, 3], 'target': 1},
                    {'PID': 12345, 'numerics': [[None, None], [None, None], [1, 1], [1, 1], [None, None]], 'codes': [[2, 3], [2, 3, 4], [], [], [4]], 'to_event': [1, 3, 4, 5, 6], 'target': 1},
                    {'PID': 12345, 'numerics': [[None, None], [None, None], [1, 1], [1, 1], [None, None], [1, 3]], 'codes': [[2, 3], [2, 3, 4], [], [], [4], [2, 3, 4]], 'to_event': [1, 3, 4, 5, 6, 7], 'target': 0}]
        actual = self.evaluator.evaluate_timeline_for_training_rows(self.timeline, self.datadict)

        assert_equals(expected, actual)
