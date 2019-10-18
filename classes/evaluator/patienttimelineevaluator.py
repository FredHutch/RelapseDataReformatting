import datetime as dt
import logging
from classes.collection.patienttimeline import PatientTimeline
from classes.collection.eventday import EventDay
from classes.collection.decisionpoint import DecisionPoint
from classes.event.treatmentencounter import TreatmentEncounter
from collections import defaultdict
from typing import List

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class PatientTimelineEvaluator:
    """
    This represents the first attempt at training evaluation (2019 JUL 29)

    """
    DECISION_POINT_LABELS = ["Death", "Morph","MRD"]
    class Context:
        """
        keep track of previous decision points for determining target status
        """
        def __init__(self):
            self.event_days = []
            self.prev_treatment = None

        def last_treatments(self):

            return

        def add_eventday(self, day: EventDay):
            self.event_days.append(day)
            relevant_codes = self.relevant_codes(day.features)
            if relevant_codes:
                self.prev_treatment = relevant_codes

        def relevant_codes(self, codes):
            """
            given a list of event/encounter features, returns a subset of the features
            that are deemed relevant to the context
            :param codes: list or set of event features
            :return: subset of features that are relevant for context
            """
            return codes

        def mrd_relapse(self):
            return any(ed.mrd_relapse() for ed in self.event_days)

    def __init__(self, induction_timewindow: int = 90, mrd_timewindow: int = 365,
                 consolidation_timewindow: int = 365, dpoint_eval_window: int = 7,
                 dpoint_positive_labels: List[str] = DECISION_POINT_LABELS):
        self.induction_timewindow = dt.timedelta(days=induction_timewindow)
        self.mrd_response_timewindow = dt.timedelta(days=mrd_timewindow)
        self.consolidation_timewindow = dt.timedelta(days=consolidation_timewindow)
        self.decision_point_consolidation_window = dt.timedelta(days=dpoint_eval_window)
        self.context = self.Context()
        self.INDUCTION_TO_EVALUATION_TIMEWINDOW = defaultdict(lambda: self.induction_timewindow,
                                                              {
                                                              TreatmentEncounter.INDICATION_INDUCTION: self.induction_timewindow,
                                                              TreatmentEncounter.INDICATION_MRD_TREATMENT: self.mrd_response_timewindow,
                                                              TreatmentEncounter.INDICATION_CONSOLIDATION_CR: self.consolidation_timewindow,
                                                              TreatmentEncounter.INDICATION_MAINTENANCE_CR: self.consolidation_timewindow,
                                                              TreatmentEncounter.INDICATION_OTHER_INDICATION: None,
                                                              })
        self.dpoint_positive_labels = dpoint_positive_labels


    def evaluate(self, timeline: PatientTimeline):
        ordered_days = timeline.get_sorted_events()
        decision_points = []
        for day in ordered_days:
            if self.is_decision_point(day):
                decision_points.append(DecisionPoint(timeline.patientid, day))
        logger.debug(("Before Consolidation, {} Decision Points were found for Patient {}".format(len(decision_points),
                                                                                                  timeline.patientid)))
        decision_points = self.consolidate_decision_pts(timeline, decision_points)
        logger.info(("After Consolidation, {} Decision Points were found for Patient {}".format(len(decision_points),
                                                                                                timeline.patientid)))
        self.assign_labels(timeline, decision_points)

        return decision_points

    def consolidate_decision_pts(self, timeline: PatientTimeline, decisionpts: List[DecisionPoint]):
        """
        Performs consolidation logic on a list of decision points
        -if two decision points are within the consolidation window of each other,
         treat them as one decision point
        -recursively perform this until it is no longer possible.
        :param timeline: the supporting PatientTimeline
        :param decisionpts: a list of DecisionPoint
        :return: a list of DecisionPoint
        """
        consolidated_dpts = []
        for pt in decisionpts:
            if not consolidated_dpts:
                consolidated_dpts.append(pt)
                continue

            # if the current decision point and the previous decision point are within the window for consolidation
            # AND there are no intervening events
            if (pt.eval_date - consolidated_dpts[-1].eval_date) <= self.decision_point_consolidation_window and not any(
                    ed.relapse() for ed in timeline.get_events_in_range(consolidated_dpts[-1].eval_date, pt.eval_date)):
                msg = "DecisionPoint Consolidation Event: adding Decision Point {new}" \
                      " to preceeding DecisionPoint {old}".format(
                        new=pt, old=consolidated_dpts[-1])
                logger.debug(msg)
                consolidated_dpts[-1].add_event_day(pt.eventdays)
            else:
                consolidated_dpts.append(pt)

        return consolidated_dpts

    def is_decision_point(self, day: EventDay):
        if day.is_decision_point():
            return True
        return False

    def assign_labels(self, timeline: PatientTimeline, decision_points: List[DecisionPoint]):
        """
        for a patient timeline and a list of decision points corresponding to it,
         determine and assign the correct labels to each decision point
        :param timeline: A Patient Timeline
        :param decision_points: A List of DecisionPoint's generated from timeline
        :return: decision_points, with labels assigned
        """
        for dpt in decision_points:
            context = self.Context()
            target_days = timeline.get_events_after_date(dpt.eval_date)
            evaluation_timewindow =  self.INDUCTION_TO_EVALUATION_TIMEWINDOW[self._most_relevant_indication(dpt.indications)]
            for target_day in target_days:
                context.add_eventday(target_day)
                cause = self.target_eval(dpt, target_day, evaluation_timewindow, context)
                if cause is not None:
                    logger.info(
                        "Decision Point Positive Label was found. PatientId: {pid} LabelDate: {dt} Decision Point: {dp}"
                        "  Target Day: {ed} Context: {c}  Cause: {cause}".format(
                            pid=timeline.patientid, dt=target_day.date, dp=dpt, ed=target_day, c=context, cause=cause))
                    dpt.label_cause = cause
                    dpt.label = cause in self.dpoint_positive_labels
                    dpt.target_date = target_day.date
                    break
            if dpt.label_cause is None:   # no valid positive label rule found
                logger.info(
                    "Decision Point Negative Label assigned to PatientId: {pid} Decision Point: {dp}".format(pid=timeline.patientid,
                                                                                              dp=dpt))
                dpt.label = False

    def target_eval(self, dpt: DecisionPoint, day: EventDay, evaluation_timewindow: dt.timedelta, context: Context):
        """
        Return a cause IFF occurs within the decision window:
            -the patient Died with the decision window
            -the patient relapsed within the decision window
            -The patient had no response to the treatment AND the Treatment regimen changes
                 Krakow AUG20: change of treatment AND indication IS Treatment/ of MRD.
        or the following occurs within a year:
            -the patient relapsed from MRD within decision window AND there was a change in Tx within a year
        :param dpt:
        :param day:
        :param context:
        :return: String Representation of positive label reason or None
        """
        time_window = day.date - dpt.eval_date
        logging.debug(
            "DecisionPoint: {dp} Compared EventDay: {ed} Evaluation Time Window: {etw} Provided Context: {c}".format(
                dp=dpt, ed=day, etw=evaluation_timewindow, c=context))
        if time_window <= evaluation_timewindow:
            if day.died():
                return "Death"
            if day.morphological_relapse():
                return 'Morph'
            if any(treatment not in dpt.treatments for treatment in day.treatments) and (
                    {TreatmentEncounter.INDICATION_INDUCTION, TreatmentEncounter.INDICATION_MRD_TREATMENT} & day.indications):
                return 'MRD'

        return None

    def _most_relevant_indication(self, indications):
        priority_list = [TreatmentEncounter.INDICATION_INDUCTION,
                           TreatmentEncounter.INDICATION_MRD_TREATMENT,
                           TreatmentEncounter.INDICATION_CONSOLIDATION_CR,
                           TreatmentEncounter.INDICATION_MAINTENANCE_CR,
                           TreatmentEncounter.INDICATION_OTHER_INDICATION,
                          ]

        for indication in priority_list:
            if indication in indications:
                return indication

        logger.warning("Alert! No valid Indication found in Indications: {ind} Returning Default".format(ind=indications))
        return None
