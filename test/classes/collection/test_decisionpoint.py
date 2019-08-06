import nose
from nose import with_setup
from classes.collection.decisionpoint import DecisionPoint
from datetime import datetime, timedelta
from classes.event.encounter import Encounter
from classes.collection.eventday import EventDay
from classes.event.relapseencounter import RelapseEncounter
from classes.event.treatmentencounter import TreatmentEncounter

from test import _make_event_day

class TestDecisionPoint:

    def setup(self):
        self.PID = 12345
        self.EVENT_DATE_ONE = datetime.strptime("7-11-2019", '%m-%d-%Y')
        e1 = RelapseEncounter(self.PID, self.EVENT_DATE_ONE, 3, 1, relapse_or_response=1, relapse_presentation=1)
        self.ed1 = _make_event_day(self.PID, self.EVENT_DATE_ONE, event_days=[e1])

        e2 = RelapseEncounter(self.PID, self.EVENT_DATE_ONE + timedelta(days=1), 3, 1, relapse_or_response=1,
                              relapse_presentation=1)
        e3 = RelapseEncounter(self.PID, self.EVENT_DATE_ONE + timedelta(days=1), 3, 1, relapse_or_response=1,
                              relapse_presentation=3)
        self.ed2 = _make_event_day(self.PID, self.EVENT_DATE_ONE + timedelta(days=1), event_days=[e2,e3])

        e4 = TreatmentEncounter(self.PID, self.EVENT_DATE_ONE + timedelta(days=2), 3, 1, hydroxyurea=1, consolidation_chemo=1)
        e5 = TreatmentEncounter(self.PID, self.EVENT_DATE_ONE + timedelta(days=2), 3, 1, hydroxyurea=1,
                                consolidation_chemo=1)
        e6 = TreatmentEncounter(self.PID, self.EVENT_DATE_ONE + timedelta(days=3), 3, 1, cytokine=1)
        self.ed3 = _make_event_day(self.PID, self.EVENT_DATE_ONE + timedelta(days=2), event_days=[e4, e5])
        self.ed4 = _make_event_day(self.PID, self.EVENT_DATE_ONE + timedelta(days=3), event_days=[e6])
        self.dpt1 = DecisionPoint(eventdays=[])

    def test_decisionpoint_evaldate(self):
        self.dpt1.add_event_day(self.ed1)

        assert self.dpt1.eval_date == datetime(2019, 7, 11, 0, 0)

    def test_decisionpoint_evaldate_multiday(self):
        self.dpt1.add_event_day(self.ed1)
        self.dpt1.add_event_day(self.ed2)

        assert self.dpt1.eval_date == datetime(2019, 7, 12, 0, 0)

    def test_decisionpoint_treatments_no_treatments(self):
        self.dpt1.add_event_day(self.ed1)

        assert sorted(self.dpt1.treatments) == []

    def test_decisionpoint_treatments_single_day(self):
        self.dpt1.add_event_day(self.ed3)

        assert sorted(self.dpt1.treatments) == ['consolidation_chemo', 'hydroxyurea']

    def test_decisionpoint_treatments_multi_day(self):
        self.dpt1.add_event_day(self.ed3)
        self.dpt1.add_event_day(self.ed4)

        assert sorted(self.dpt1.treatments) == ['consolidation_chemo', 'cytokine', 'hydroxyurea']

if __name__ == '__main__':
    nose.run()