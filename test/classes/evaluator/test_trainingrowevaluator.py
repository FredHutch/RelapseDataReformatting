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
