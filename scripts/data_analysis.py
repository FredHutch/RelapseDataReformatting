import json
import logging
import numpy as np
import pandas as pd
import os

from sklearn.model_selection import GroupKFold
from collections import defaultdict
from redcap import Project, RedcapError

from classes import map_instrument_df_to_class
from classes.collection.eventday import EventDay
from classes.collection.patienttimeline import PatientTimeline
from classes.evaluator.patienttimelineevaluator import PatientTimelineEvaluator
from classes.evaluator.trainingrowevaluator import TrainingRowEvaluator

import scripts.map_categorical_features as ddict
from scripts import GATEWAY_FEATURE_RECODE_MAP, BUCKETS
from scripts.reformat_relapse_data import pull_from_red_cap

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)





if __name__ == '__main__':
    import yaml
    import logging
    import logging.config
    import os
    import numpy as np
    import matplotlib.mlab as mlab
    import matplotlib.pyplot as plt

    cd = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(cd, '../logging.yaml'), 'r') as f:
        log_cfg = yaml.safe_load(f.read())
        logging.config.dictConfig(log_cfg)
    logger = logging.getLogger()
    config = dict()
    for c in ['../config_default.json', '../config.json']:
        with open(os.path.join(cd, c), 'r') as fin:
            config.update(json.load(fin))

    timelines = pull_from_red_cap(config)
    time_to_relapse = np.array([(dp.target_date - dp.eval_date).days
                       for timeline in timelines.values()
                       for dp in timeline.decision_points
                       if dp.label is True])
    num_bins = 50
    # the histogram of the data
    #n, bins, patches = plt.hist(time_to_relapse, num_bins, density=True, facecolor='blue', alpha=0.5)
    plt.hist(time_to_relapse, bins=num_bins)
    plt.xlabel('Days to Relapse')
    plt.ylabel('Probability')
    plt.title(r'Histogram of DtR')
    plt.grid(True)
    # Tweak spacing to prevent clipping of ylabel
    plt.subplots_adjust(left=0.15)
    plt.show()
