import datetime as dt
from classes.collection.patienttimeline import PatientTimeline
from classes.collection.eventday import EventDay
from classes.collection.decisionpoint import DecisionPoint

from typing import List


class PatientTimelineEvaluator:
    """
    This represents the first attempt at training evaluation (2019 JUL 29)

    """
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


    def __init__(self, timewindow: int, dpoint_eval_window: int):
        self.target_timewindow = dt.timedelta(days=timewindow)
        self.mrd_response_timewindow = dt.timedelta(days=365)
        self.decision_point_consolidation_window = dt.timedelta(days=dpoint_eval_window)
        self.context = self.Context()

    def evaluate(self, timeline: PatientTimeline):
        ordered_days = timeline.get_sorted_events()
        decision_points = []
        for day in ordered_days:
            if self.is_decision_point(day):
                decision_points.append(DecisionPoint(day))

        decision_points = self.consolidate_decision_pts(timeline, decision_points)
        self.assign_labels(timeline, decision_points)

        return decision_points

    def consolidate_decision_pts(self, timeline: PatientTimeline, decisionpts: List[DecisionPoint]):
        """
        Performs consolidation logic on a list of decision points
        -if two decision points are within the consolidation window of each other,
         treat them as one decision point
        -recursively perform this until it is no longer possible.
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
                consolidated_dpts[-1].add_event_day(pt.eventdays)
            else:
                consolidated_dpts.append(pt)

        return consolidated_dpts

    def is_decision_point(self, day: EventDay):
        if day.treatments:
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

            for target_day in target_days:
                context.add_eventday(target_day)
                cause = self.target_eval(dpt, target_day, context)
                if cause is not None:
                    dpt.label_cause = cause
                    dpt.label = True
                    break
            if dpt.label_cause is None: # no valid positive label rule found
                dpt.label = False

    def target_eval(self, dpt: DecisionPoint, day: EventDay, context: Context):
        """
        Return a cause IFF occurs within the decision window:
            -the patient Died with the decision window
            -the patient relapsed within the decision window
            -The patient had no response to the treatment AND
        or the following occurs within a year:
            -the patient relapsed from MRD within decision window AND there was a change in Tx within a year
        :param day:
        :return:
        """
        time_window = day.date - dpt.eval_date
        if time_window <= self.target_timewindow:
            if day.died():
                return "Death"
            if day.morphological_relapse():
                return "Morphological Relapse"
            if day.treatments != dpt.treatments:
                return "No Response + New Tx"
        if time_window <= self.mrd_response_timewindow:
            if context.mrd_relapse() and day.treatments != dpt.treatments:
                return "MRD Relapse + Tx Change"

        return None




