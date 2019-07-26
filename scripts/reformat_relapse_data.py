from collections import defaultdict
import json
import logging
import os
import pandas
from classes import map_instrument_df_to_class

from redcap import Project, RedcapError

NON_REPEAT_FORMS = set(['vital_status', 'patient_id'])

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
    form_df = dict()

    timelines = defaultdict(dict)
    for form in project.forms:
        try:
            intermediate_df = project.export_records(forms=[form], format='df')

            '''
            vital status and person_id information is included by default in most instruments
            and appears as an extra row with *mostly* empty columns
            we are dropping it for profiling purposes since it throws the counts/correlations off.
            '''
            form_df[form] = intermediate_df
            if form not in NON_REPEAT_FORMS:
                form_df[form] = intermediate_df.loc[intermediate_df['redcap_repeat_instrument'].notnull()]
        except RedcapError:
            print("Failure to export records from REDCap for form: {}".format(form))
            continue

        events = map_instrument_df_to_class(form_df[form])
        for event in events:
            if event.date not in timelines[event.patientid].keys():
                timelines[event.patientid][event.date] = EventDay(event.patientid, event.date)
            .append(event)



