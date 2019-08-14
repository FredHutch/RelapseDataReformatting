from collections import defaultdict
import json
import logging
from classes import map_instrument_df_to_class
from classes.collection.eventday import EventDay
from classes.collection.patienttimeline import PatientTimeline
from classes.evaluator.patienttimelineevaluator import PatientTimelineEvaluator
from redcap import Project, RedcapError

NON_REPEAT_FORMS = {'vital_status', 'patient_id'}

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def pull_from_red_cap(config):
    """
    pull data from the Relapse REDCap project, load into dataframe
    *for now* output file to temporary csv
    """
    URL = config["RED_CAP_ENGINE"]["URL"]
    API_KEY = config["RED_CAP_ENGINE"]["API"]
    project = Project(URL, API_KEY)
    patient_eds = defaultdict(dict)

    for form in project.forms:
        try:
            intermediate_df = project.export_records(forms=[form], format='df')
        except RedcapError:
            print("Failure to export records from REDCap for form: {}".format(form))
            continue
        events = map_instrument_df_to_class(form, intermediate_df)

        for event in events:
            if event.date not in patient_eds[event.patientid].keys():
                patient_eds[event.patientid][event.date] = EventDay(event.patientid, event.date, event)
            else:
                patient_eds[event.patientid][event.date].add_event(event)

    evaluator = PatientTimelineEvaluator(timewindow=90, dpoint_eval_window=10)
    timelines = dict()
    for patientid, event_days in patient_eds.items():
        timelines[patientid] = PatientTimeline(patientid, list(event_days.values()))
        decision_pts = evaluator.evaluate(timelines[patientid])
        timelines[patientid].decision_points = decision_pts
        print("decision points for patient {} timeline: {}".format(patientid, timelines[patientid].decision_points))






if __name__ == '__main__':
    with open('../config.json') as fin:
        config = json.load(fin)
    pull_from_red_cap(config)