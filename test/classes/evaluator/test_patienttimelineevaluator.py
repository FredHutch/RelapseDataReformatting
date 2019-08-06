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
        self.TIME_WINDOW = 5
        self.DPOINT_WINDOW = 50
        self.INDEX_EPOCH = 1
        self.INDEX_RELAPSE = 2

        e1 = DemographicsEncounter(self.PID, self.EVENT_DATE_ONE, self.INDEX_EPOCH, self.INDEX_RELAPSE, hydroxyurea=1,
                                consolidation_chemo=1)
        e2 = TreatmentEncounter(self.PID, self.EVENT_DATE_ONE, self.INDEX_EPOCH,
                                self.INDEX_RELAPSE, hydroxyurea=1,
                                consolidation_chemo=1)
        e3 = TreatmentEncounter(self.PID, self.EVENT_DATE_ONE + timedelta(days=2), self.INDEX_EPOCH + 2,
                                self.INDEX_RELAPSE + 2, hydroxyurea=1, cytokine=1,
                                consolidation_chemo=1)
        e4 = RelapseEncounter(self.PID, self.EVENT_DATE_ONE + timedelta(days=3), self.INDEX_EPOCH + 3,
                                self.INDEX_RELAPSE + 3, relapse_or_response=1, relapse_presentation=1)
        e5 = RelapseEncounter(self.PID, self.EVENT_DATE_ONE + timedelta(days=4), self.INDEX_EPOCH + 4,
                              self.INDEX_RELAPSE + 4, relapse_or_response=1,
                              relapse_presentation=1)
        e6 = TreatmentEncounter(self.PID, self.EVENT_DATE_ONE + timedelta(days=5), self.INDEX_EPOCH + 5,
                                self.INDEX_RELAPSE + 5, cytokine=1)
        e7 = RelapseEncounter(self.PID, self.EVENT_DATE_ONE + timedelta(days=5), self.INDEX_EPOCH + 5,
                              self.INDEX_RELAPSE + 5, relapse_or_response=1,
                              relapse_presentation=3)
        e8 = TreatmentEncounter(self.PID, self.EVENT_DATE_ONE + timedelta(days=6), self.INDEX_EPOCH + 6,
                                self.INDEX_RELAPSE + 6, cytokine=1)
        e9 = VitalsEncounter(self.PID, self.EVENT_DATE_ONE + timedelta(days=106), self.INDEX_EPOCH + 106,
                                self.INDEX_RELAPSE + 106, )



        self.ed1 = _make_event_day(self.PID, self.EVENT_DATE_ONE, event_days=[e1, e2])
        self.ed2 = _make_event_day(self.PID, self.EVENT_DATE_ONE + timedelta(days=2), event_days=[e3])
        self.ed3 = _make_event_day(self.PID, self.EVENT_DATE_ONE + timedelta(days=3), event_days=[e4])
        self.ed4 = _make_event_day(self.PID, self.EVENT_DATE_ONE + timedelta(days=4), event_days=[e5])
        self.ed5 = _make_event_day(self.PID, self.EVENT_DATE_ONE + timedelta(days=5), event_days=[e6, e7])
        self.ed6 = _make_event_day(self.PID, self.EVENT_DATE_ONE + timedelta(days=6), event_days=[e8])
        self.ed7 = _make_event_day(self.PID, self.EVENT_DATE_ONE + timedelta(days=106), event_days=[e9])


        self.evaluator = pte.PatientTimelineEvaluator(self.TIME_WINDOW, self.DPOINT_WINDOW)
        self.timeline = _make_timeline([self.ed1, self.ed2, self.ed3, self.ed4, self.ed5, self.ed6, self.ed7])

    def _make_encounter_with_timeshift(self, enc, pid, date, epoch, relapse, offset=0, **kwargs):
        return enc(pid, date + timedelta(days=offset), epoch + offset, relapse + offset, **kwargs)

    def test_pte_evaluate(self):
        dpt1 = DecisionPoint(eventdays=[self.ed1, self.ed2])
        dpt1.label_cause = 'Morphological Relapse'
        dpt1.label = True
        dpt2 = DecisionPoint(eventdays=[self.ed5])

        dpt2.label = True


        actual_dpts = self.evaluator.evaluate(self.timeline)

        assert_equals(actual_dpts, [dpt1, dpt2])

    def test_assign_labels(self):
        return

    def test_target_eval_mr(self):
        dpt1 = DecisionPoint(eventdays=[self.ed1, self.ed2])
        context = pte.PatientTimelineEvaluator.Context()
        context.add_eventday(self.ed4)

        expected = 'Morphological Relapse'
        target = self.evaluator.target_eval(dpt1, self.ed4, context)
        assert_equals(expected, target)

    def test_target_eval_death(self):
        death_encounter = self._make_encounter_with_timeshift(VitalsEncounter, self.PID, self.EVENT_DATE_ONE,
                                                              self.INDEX_EPOCH,
                                                              self.INDEX_RELAPSE, 4, death_status=1)
        self.ed4.add_event(death_encounter)
        dpt1 = DecisionPoint(eventdays=[self.ed1, self.ed2])
        context = pte.PatientTimelineEvaluator.Context()
        context.add_eventday(self.ed4)

        expected = 'Death'
        target = self.evaluator.target_eval(dpt1, self.ed4, context)
        assert_equals(expected, target)

    def test_target_eval_nr_and_tx_change(self):
        dpt1 = DecisionPoint(eventdays=[self.ed1, self.ed2])
        context = pte.PatientTimelineEvaluator.Context()
        tx_change_enc =  self._make_encounter_with_timeshift(TreatmentEncounter, self.PID, self.EVENT_DATE_ONE,
                                                              self.INDEX_EPOCH,
                                                              self.INDEX_RELAPSE, 5, cytokine=1)
        tx_change_day = _make_event_day(self.PID, self.EVENT_DATE_ONE + timedelta(days=5), event_days=[tx_change_enc])
        context.add_eventday(tx_change_day)

        expected = 'No Response + New Tx'
        target = self.evaluator.target_eval(dpt1, tx_change_day, context)
        assert_equals(expected, target)

    def test_target_eval_long_mrd_and_tx_change(self):
        dpt1 = DecisionPoint(eventdays=[self.ed1, self.ed2])
        context = pte.PatientTimelineEvaluator.Context()
        tx_change_enc = self._make_encounter_with_timeshift(TreatmentEncounter, self.PID, self.EVENT_DATE_ONE,
                                                            self.INDEX_EPOCH,
                                                            self.INDEX_RELAPSE, 100, cytokine=1)
        tx_change_day = _make_event_day(self.PID, self.EVENT_DATE_ONE + timedelta(days=5), event_days=[tx_change_enc])
        context.add_eventday(tx_change_day)

        expected = 'No Response + New Tx'
        target = self.evaluator.target_eval(dpt1, tx_change_day, context)
        assert_equals(expected, target)



if __name__ == '__main__':
    nose.run()