import json
import logging
import pandas as pd
import os

from collections import defaultdict
from redcap import Project, RedcapError
from classes import map_instrument_df_to_class
from classes.collection.eventday import EventDay
from classes.collection.patienttimeline import PatientTimeline
from classes.evaluator.patienttimelineevaluator import PatientTimelineEvaluator


import scripts.map_categorical_features as ddict
from scripts.map_categorical_features import gateway_feature_recode_map

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def pull_gateway_data(config):
    '''
    pull gateway data related to hematapoetic cell transplant
    from static csv
    '''
    gateway_df = pd.read_csv(config['GATEWAY_DATA'])
    # recode uwid
    gateway_df['uwid'] = gateway_df['uwid'].map(lambda x: int(x.lstrip('U')))
    # define female_donor_male_recipient
    gateway_df['female_donor_male_recipient'] = gateway_df.eval("donsex == 'Female' and sex == 'Male'").astype(int)
    # recode features
    gateway_df = recode_features(gateway_df, gateway_feature_recode_map)
    gateway_df = pd.get_dummies(gateway_df,prefix=['cmvx','hla_cco','tbidose','celltxl'], \
                                columns = ['cmvx','hla_cco','tbidose','celltxl'])
    # one-hot encode proplbl
    proplbl = gateway_df.proplbl.str.split(r'\s*,\s*', expand=True).apply(pd.Series.value_counts, 1).fillna(0, downcast='infer').add_prefix('proplbl_')
    gateway_df = pd.concat([gateway_df.drop(['proplbl'], axis=1), proplbl], axis=1, sort=False)
    gateway_df = gateway_df.drop(columns = ['upn','txdatex', 'prexlbl', 'agvhday', \
                                            'don_drm', 'don_mat','birthdat','agvhdat',\
                                            'agvhgrd','agvhskn','agvhlvr','agvhgut', \
                                            'don1sex', 'don2sex', 'sex', 'donsex'])
    return gateway_df




def get_values(elements, lookups):
    """
    get value from lookup dictionary
    """
    if isinstance(elements, float):
        if pd.isna(elements):
            return None
        return lookups.get(str(int(elements)))
    elif isinstance(elements, str):
        if len(elements.split(',')) == 1:
            return lookups.get(elements)
        elif len(elements.split(',')) > 1:
            element_parts = elements.split(',')
            new_list = [lookups.get(i) for i in element_parts if lookups.get(i)]
            return ','.join(set(new_list))
    else:
        return None

def recode_features(df, lookups):
    """
    update column values in-place
    :param df: pandas dataframe
    :param lookups: dictionary
    :return: None.
    """
    # columns to recode
    cols = list(lookups.keys())
    for col in cols:
        df[col] = df[col].apply(lambda x: get_values(x, lookups[col]))
    return df


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
            logger.warning("Failure to export records from REDCap for form: {}".format(form))
            continue
        
        events = map_instrument_df_to_class(form, intermediate_df)
        if form == 'patient_id': 
            gateway_df = pull_gateway_data(config)
            events += map_instrument_df_to_class('gateway_encounter', gateway_df)
        for event in events:
            if event.date not in patient_eds[event.patientid].keys():
                patient_eds[event.patientid][event.date] = EventDay(event.patientid, event.date, event)
            else:
                patient_eds[event.patientid][event.date].add_event(event)

    evaluator = PatientTimelineEvaluator(induction_timewindow=90, mrd_timewindow=365,
                                          consolidation_timewindow=365, dpoint_eval_window=7)
    timelines = dict()
    sum_dps = 0
    for patientid, event_days in patient_eds.items():
        timelines[patientid] = PatientTimeline(patientid, list(event_days.values()))
        decision_pts = evaluator.evaluate(timelines[patientid])
        logger.info("number of decision points for patient {} on timeline: {}".format(patientid, len(decision_pts)))
        timelines[patientid].decision_points = decision_pts
        logger.info("decision points for patient {} timeline: {}".format(patientid, timelines[patientid].decision_points))
        sum_dps += len(timelines[patientid].decision_points)

    tot_pat = len(timelines.keys())
    logger.info("Total Patients: {}".format(tot_pat))
    logger.info("Total Decision Points: {}".format(sum_dps))
    sum_pat = sum([1 for p, t in timelines.items() if t.decision_points])
    logger.info("Total Patients with Decision Points: {}".format(sum_pat))
    logger.info("AVG Decision Points per Patient: {num}/{den} = {avg}".format(num=sum_dps, den=tot_pat,
                                                                              avg=(sum_dps / tot_pat)))

    logger.info("AVG Decision Points per Patient who had a Decision Point: {num}/{den} = {avg}".format(num=sum_dps, den=sum_pat,
                                                                              avg=(sum_dps / sum_pat)))
    tot_time_btw = sum([t.get_time_between_decision_points() for _,t in timelines.items()])
    logger.info("AVG Time between Decision Points in days: {num}/{den} = {avg}".format(num=tot_time_btw, den=sum_dps,
                                                                              avg=(tot_time_btw / sum_dps)))

    data_dict_pkl_path = os.path.realpath(config["DATA_DICTIONARY"]["data_dict"])
    data_dict_csv_path = os.path.realpath(config["DATA_DICTIONARY"]["data_dict_csv"])
    categorical_feature_path = os.path.realpath(config["DATA_DICTIONARY"]["categorical_feature"])
    data_dict = ddict.DataDictionary(data_dict_csv_path, data_dict_pkl_path)

if __name__ == '__main__':
    import yaml
    import datetime as dt
    import logging
    import logging.config
    import os

    with open(os.path.realpath('logging.yaml'), 'r') as f:
        log_cfg = yaml.safe_load(f.read())
        log_cfg['handlers']['file']['filename'] = 'RelapseDataFormatting_{}.log'.format(dt.datetime.now().date())
        logging.config.dictConfig(log_cfg)
    logger = logging.getLogger(__name__)


    with open(os.path.realpath('config.json')) as fin:
        config = json.load(fin)
    pull_from_red_cap(config)
