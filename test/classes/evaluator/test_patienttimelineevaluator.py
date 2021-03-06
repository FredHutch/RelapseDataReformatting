import datetime as dt
import nose
from nose import with_setup
from nose.tools import assert_equals, assert_in

from classes.collection.decisionpoint import DecisionPoint
from datetime import datetime, timedelta
from classes.event.encounter import Encounter
from classes.collection.eventday import EventDay
from classes.event.relapseencounter import RelapseEncounter
from classes.event.treatmentencounter import TreatmentEncounter
from classes.event.demographicsencounter import DemographicsEncounter
from classes.event.vitalsencounter import VitalsEncounter

from test import _make_event_day, _make_timeline

import classes.evaluator.patienttimelineevaluator as pte

class TestPatientTimelineEvaluator:
    def setup(self):
        self.PID = 12345
        self.EVENT_DATE_ONE = datetime.strptime("7-11-2019", '%m-%d-%Y')
        self.EVENT_START_DATE_ONE = datetime.strptime("7-11-2019", '%m-%d-%Y')
        self.TIME_WINDOW = 5
        self.LONG_TIME_WINDOW = 100
        self.DPOINT_WINDOW = 50
        self.INDEX_EPOCH = 1
        self.INDEX_RELAPSE = 2

        e1 = self._make_encounter_with_timeshift(DemographicsEncounter, self.PID, self.EVENT_DATE_ONE,
                                                            self.INDEX_EPOCH,
                                                            self.INDEX_RELAPSE, hydroxyurea=1, consolidation_chemo=1)
        e2 = self._make_treatment_encounter_with_timeshift(TreatmentEncounter, self.PID, self.EVENT_DATE_ONE, self.EVENT_START_DATE_ONE,
                                                            self.INDEX_EPOCH,
                                                            self.INDEX_RELAPSE, hydroxyurea=1, consolidation_chemo=1)
        e3 = self._make_treatment_encounter_with_timeshift(TreatmentEncounter, self.PID, self.EVENT_DATE_ONE, self.EVENT_START_DATE_ONE,
                                                            self.INDEX_EPOCH,
                                                            self.INDEX_RELAPSE, 2, hydroxyurea=1, cytokine=1,
                                                            consolidation_chemo=1)
        e4 = self._make_encounter_with_timeshift(RelapseEncounter, self.PID, self.EVENT_DATE_ONE,
                                                            self.INDEX_EPOCH,
                                                            self.INDEX_RELAPSE, 3, relapse_or_response=1, relapse_presentation=1)
        e5 = self._make_encounter_with_timeshift(RelapseEncounter, self.PID, self.EVENT_DATE_ONE,
                                                            self.INDEX_EPOCH,
                                                            self.INDEX_RELAPSE, 4, relapse_or_response=1,
                                                            relapse_presentation=1)
        e6 = self._make_treatment_encounter_with_timeshift(TreatmentEncounter, self.PID, self.EVENT_DATE_ONE, self.EVENT_START_DATE_ONE,
                                                            self.INDEX_EPOCH,
                                                            self.INDEX_RELAPSE,  5, cytokine=1, rx_indication=TreatmentEncounter.INDICATION_MRD_TREATMENT)
        e7 = self._make_encounter_with_timeshift(RelapseEncounter, self.PID, self.EVENT_DATE_ONE,
                                                            self.INDEX_EPOCH,
                                                            self.INDEX_RELAPSE, 6, relapse_or_response=1,
                                                            relapse_presentation=3)
        e8 = self._make_treatment_encounter_with_timeshift(TreatmentEncounter, self.PID, self.EVENT_DATE_ONE, self.EVENT_START_DATE_ONE,
                                                            self.INDEX_EPOCH,
                                                            self.INDEX_RELAPSE,  6, cytokine=1, hypomethylating=1, rx_indication=TreatmentEncounter.INDICATION_MRD_TREATMENT)
        e9 = self._make_encounter_with_timeshift(VitalsEncounter, self.PID, self.EVENT_DATE_ONE,
                                                            self.INDEX_EPOCH,
                                                            self.INDEX_RELAPSE, 105)

        self.ed1 = _make_event_day(self.PID, self.EVENT_DATE_ONE, event_days=[e1, e2])
        self.ed2 = _make_event_day(self.PID, self.EVENT_DATE_ONE + timedelta(days=2), event_days=[e3])
        self.ed3 = _make_event_day(self.PID, self.EVENT_DATE_ONE + timedelta(days=3), event_days=[e4])
        self.ed4 = _make_event_day(self.PID, self.EVENT_DATE_ONE + timedelta(days=4), event_days=[e5])
        self.ed5 = _make_event_day(self.PID, self.EVENT_DATE_ONE + timedelta(days=5), event_days=[e6])
        self.ed6 = _make_event_day(self.PID, self.EVENT_DATE_ONE + timedelta(days=6), event_days=[e7, e8])
        self.ed7 = _make_event_day(self.PID, self.EVENT_DATE_ONE + timedelta(days=105), event_days=[e9])


        self.evaluator = pte.PatientTimelineEvaluator()
        self.timeline = _make_timeline(self.PID, [self.ed1, self.ed2, self.ed3, self.ed4, self.ed5, self.ed6, self.ed7])

    def _make_encounter_with_timeshift(self, enc, pid, date, epoch, relapse, offset=0, **kwargs):
        return enc(pid, date + timedelta(days=offset), epoch + offset, relapse + offset, **kwargs)

    def _make_treatment_encounter_with_timeshift(self, enc, pid, date, start_date, epoch, relapse, offset=0, **kwargs):
        return enc(pid, date + timedelta(days=offset), start_date + timedelta(days=offset), epoch + offset,
                   relapse + offset, **kwargs)


    def test_pte_evaluate(self):
        dpt1 = DecisionPoint(patientid=self.PID, eventdays=[self.ed1, self.ed2])
        dpt1.label_cause = 'Morphological Relapse'
        dpt1.label = True
        dpt2 = DecisionPoint(patientid=self.PID, eventdays=[self.ed5])
        dpt2.label_cause = "Induction/MRD Indication + New Tx"
        dpt2.label = True
        dpt3 = DecisionPoint(patientid=self.PID, eventdays=[self.ed6])
        dpt3.label_cause = None
        dpt3.label = False

        actual_dpts = self.evaluator.evaluate(self.timeline)
        assert_equals(actual_dpts, [dpt1, dpt2, dpt3])

    def test_consolidate_decision_points(self):
        dpt1 = DecisionPoint(patientid=self.PID, eventdays=[self.ed1])
        dpt2 = DecisionPoint(patientid=self.PID, eventdays=[self.ed2])
        dpt3 = DecisionPoint(patientid=self.PID, eventdays=[self.ed5])
        dpt4 = DecisionPoint(patientid=self.PID, eventdays=[self.ed6])

        merged_dpt1 = DecisionPoint(patientid=self.PID, eventdays=[self.ed1, self.ed2])
        merged_dpt2 = DecisionPoint(patientid=self.PID, eventdays=[self.ed5])
        merged_dpt3 = DecisionPoint(patientid=self.PID, eventdays=[self.ed6])

        actual_dpts = self.evaluator.consolidate_decision_pts(self.timeline, [dpt1, dpt2, dpt3, dpt4])
        assert_equals(actual_dpts, [merged_dpt1, merged_dpt2, merged_dpt3])

    def test_consolidate_decision_points_relapse_breakpoint(self):
        dpt1 = DecisionPoint(patientid=self.PID, eventdays=[self.ed5])
        dpt2 = DecisionPoint(patientid=self.PID, eventdays=[self.ed6])

        merged_dpt1 = DecisionPoint(patientid=self.PID, eventdays=[self.ed5])
        merged_dpt2 = DecisionPoint(patientid=self.PID, eventdays=[self.ed6])

        actual_dpts = self.evaluator.consolidate_decision_pts(self.timeline, [dpt1, dpt2])
        assert_equals(actual_dpts, [merged_dpt1, merged_dpt2])

    def test_assign_labels(self):
        return

    def test_target_eval_mr(self):
        dpt1 = DecisionPoint(patientid=self.PID, eventdays=[self.ed1, self.ed2])
        context = pte.PatientTimelineEvaluator.Context()
        context.add_eventday(self.ed4)

        expected = 'Morphological Relapse'
        target = self.evaluator.target_eval(dpt1, self.ed4, dt.timedelta(days=self.TIME_WINDOW), context)
        assert_equals(expected, target)

    def test_target_eval_death(self):
        import datetime as dt
        death_encounter = self._make_encounter_with_timeshift(VitalsEncounter, self.PID, self.EVENT_DATE_ONE,
                                                              self.INDEX_EPOCH,
                                                              self.INDEX_RELAPSE, 4, death_status=1)
        self.ed4.add_event(death_encounter)
        dpt1 = DecisionPoint(patientid=self.PID, eventdays=[self.ed1, self.ed2])
        context = pte.PatientTimelineEvaluator.Context()
        context.add_eventday(self.ed4)

        expected = 'Death'
        target = self.evaluator.target_eval(dpt1, self.ed4, dt.timedelta(days=self.TIME_WINDOW), context)
        assert_equals(expected, target)

    def test_target_eval_tx_drop_no_additions(self):
        dpt1 = DecisionPoint(patientid=self.PID, eventdays=[self.ed1, self.ed2])
        context = pte.PatientTimelineEvaluator.Context()
        tx_change_enc =  self._make_treatment_encounter_with_timeshift(TreatmentEncounter, self.PID, self.EVENT_DATE_ONE, self.EVENT_START_DATE_ONE,
                                                              self.INDEX_EPOCH,
                                                              self.INDEX_RELAPSE, 5, cytokine=1)
        tx_change_day = _make_event_day(self.PID, self.EVENT_DATE_ONE + timedelta(days=5), event_days=[tx_change_enc])
        context.add_eventday(tx_change_day)

        expected = None
        target = self.evaluator.target_eval(dpt1, tx_change_day, dt.timedelta(days=self.TIME_WINDOW), context)
        assert_equals(expected, target)

    def test_target_eval_long_mrd_and_tx_change(self):
        dpt1 = DecisionPoint(patientid=self.PID, eventdays=[self.ed1, self.ed2])
        context = pte.PatientTimelineEvaluator.Context()
        tx_change_enc = self._make_treatment_encounter_with_timeshift(TreatmentEncounter, self.PID, self.EVENT_DATE_ONE, self.EVENT_START_DATE_ONE,
                                                            self.INDEX_EPOCH,
                                                            self.INDEX_RELAPSE, 100, cytokine=1, hypomethylating=1, rx_indication=TreatmentEncounter.INDICATION_MRD_TREATMENT)
        mrd_relapse_enc = self._make_encounter_with_timeshift(RelapseEncounter, self.PID, self.EVENT_DATE_ONE,
                                                            self.INDEX_EPOCH,
                                                            self.INDEX_RELAPSE, 5, relapse_or_response=1,
                                                            relapse_presentation=3)
        mrd_relapse_day = _make_event_day(self.PID, self.EVENT_DATE_ONE + timedelta(days=5), event_days=[mrd_relapse_enc])
        tx_change_day = _make_event_day(self.PID, self.EVENT_DATE_ONE + timedelta(days=100), event_days=[tx_change_enc])
        context.add_eventday(mrd_relapse_day)
        context.add_eventday(tx_change_day)

        expected = 'Induction/MRD Indication + New Tx'
        target = self.evaluator.target_eval(dpt1, tx_change_day, dt.timedelta(days=self.LONG_TIME_WINDOW), context)
        assert_equals(expected, target)



if __name__ == '__main__':
    nose.run()