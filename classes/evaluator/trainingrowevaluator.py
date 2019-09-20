import logging
from operator import itemgetter
from classes.collection.patienttimeline import PatientTimeline

logger = logging.getLogger(__name__)


class TrainingRowEvaluator:
    def __init__(self):

        return

    def convert_label_to_int(self, label):
        if label:
            return 1
        return 0

    def evaluate_timeline_for_training_rows(self, timeline: PatientTimeline, datadict):
        if not timeline.decision_points:
            msg = "AttributeError: PatientTimeline for PatientId: {id} does not have DecisionPoints: {dp}".format(
                id=timeline.patientid, dp=timeline.decision_points)
            logger.warning(msg)
            raise AttributeError(msg)

        dp_rows = list()
        bad_cols = set()
        for dp in timeline.decision_points:
            visit_representations = list()
            label = dp.label
            eventdays = timeline.get_events_before_date(dp.eval_date)
            raw_feature_days = {ed.days_since_epoch: ed.existant_features for ed in eventdays}
            for day, features in raw_feature_days.items():
                rowdict = {'PID': timeline.patientid,
                           'DAY': day,
                           **features
                           }

                visit_rep, bad_cols = self.build_visit_dict(rowdict, datadict, bad_cols)
                visit_representations.append(visit_rep)
            training_row = self.create_condensed_row(timeline.patientid, visit_representations,
                                                      self.convert_label_to_int(dp.label))
            dp_rows.append(training_row)
        if bad_cols:
            msg = "Alert! The following feature names could not be processed: {cols}".format(cols=bad_cols)
            logger.warning(msg)

        return dp_rows

    def _make_wide_rows(self, row_list):
        '''
        return a tuple of:
          condensed numerics list (a list-of-lists, 1 per day)
          condensed codes list (a list of all codes that appear at least once)
        '''
        wide_row_numerics = []
        wide_row_codes = []
        wide_row_days = []
        sorted_row_list = sorted(row_list, key=itemgetter('PID', 'DAY'))
        for row in sorted_row_list:
            wide_row_numerics.append(row['numerics'])
            wide_row_codes.append(row['codes'])
            wide_row_days.append(row['DAY'])

        return wide_row_numerics, wide_row_codes, wide_row_days

    def create_condensed_row(self, pid, row_list, event_target):
        condensed_numerics, condensed_codes, condensed_days = self._make_wide_rows(row_list)
        row = {'PID': pid,
                'numerics': condensed_numerics,
                'codes': condensed_codes,
                'to_event': condensed_days,
                'target': event_target
                }

        return row

    def build_visit_dict(self, rowdict, datadict, error_cols, default_vals=None):

        newvisit = {'PID': rowdict.pop('PID'),
                    'numerics': ([None] * len(datadict.numeric_cols)),
                    'DAY': int(rowdict.pop('DAY', 0))
                    }
        codeset = set()
        for col, val in rowdict.items():    
            direct_codekey = datadict.code_cols.get(col)
            one_hot_codekey = datadict.code_mappings.get("{}_{}".format(col, int(val)))
            if col in datadict.drop_cols:
                pass
            elif direct_codekey:
                if direct_codekey[1] == 'Binary' and not val:
                    pass
                else:
                    codeset.add(datadict.code_mappings.get(col))
            elif one_hot_codekey:
                codeset.add(one_hot_codekey)
            elif col in datadict.numeric_cols:
                # change NULL values in numerics to valid default float given in config file
                # backoff to zero if column is not in config['DEFAULT_VALUES']
                if val is None and default_vals is not None:
                    try:
                        val = default_vals['DEFAULT_VALUES'][col]
                    except:
                        print("Numeric columns must be non null or contained within the DEFAULT_VALUES \
                                dictionary in config.json - Column  ({}) defaulting to 0 ".format(col))
                        val = 0
                newvisit['numerics'][datadict.numeric_cols.index(col)] = val
            else:
                error_cols.add(col)
        newvisit['codes'] = list(codeset)
        return newvisit, error_cols