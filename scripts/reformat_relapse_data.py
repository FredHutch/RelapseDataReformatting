from collections import defaultdict
import json
import logging
import os
import pandas
from classes import map_instrument_df_to_class
from classes.collection.eventday import EventDay

from redcap import Project, RedcapError

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
    timelines = defaultdict(dict)

    for form in project.forms:
        try:
            intermediate_df = project.export_records(forms=[form], format='df')
        except RedcapError:
            print("Failure to export records from REDCap for form: {}".format(form))
            continue

        events = map_instrument_df_to_class(form, intermediate_df)

        for event in events:
            if event.date not in timelines[event.patientid].keys():
                timelines[event.patientid][event.date] = EventDay(event.patientid, event.date)
            else:
                timelines[event.patientid][event.date].add_event(event)


if __name__ == '__main__':
    with open('../config.json') as fin:
        config = json.load(fin)
    pull_from_red_cap(config)