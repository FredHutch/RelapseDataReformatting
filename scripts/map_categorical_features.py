"""
create a data dictionary that maps distinct categorical or 'code' features
to unique integers for retain model training and interpretation
"""
import os
import csv
import json
import logging
import pickle

logger = logging.getLogger(__name__)


class DataDictionary():
    def __init__(self, data_dict_csv_path=None, data_dict_pkl_path=None, categorical_feature_path=None):
        self.code_cols = {}
        self.categorical_cols = {}
        self.combine_cols = []
        self.numeric_cols = []
        self.drop_cols = []
        self.code_mappings = {}        
        self.data_dict_pkl_path = data_dict_pkl_path
        self.data_dict_csv_path = data_dict_csv_path
        self.categorical_feature_path = categorical_feature_path

    def is_categorical_var(self, col, val):
        cat_val = self.categorical_cols.get(col, None)
        if cat_val and int(val) <= int(cat_val):
            cat_col = '{}_{}'.format(col, int(val))
            return cat_col, 1

        return None, None


    def create_data_dict(self):
        # initial creation of pickled data dictionary
        if self.data_dict_csv_path:
            self.read_csv_data_dict()
        else:
            logger.warning("No input path for csv feature dictionary provided")
        if self.data_dict_pkl_path:
            self.map_codes_to_ints()
        else:
            logger.warning("No output path for pickled feature mapping provided")

        if self.categorical_feature_path:
            self.load_categorical_dict()
        else:
            logger.warning("No input path for csv categorical dictionary provided")


    def load_data_dict(self):
        # read in precreated pickled data dictionary
        if self.data_dict_csv_path:
            self.read_csv_data_dict()
        else:
          logger.warning("No input path for csv feature dictionary provided")        
        if self.data_dict_pkl_path:
            self.get_code_mapping()
        else:
          logger.warning("No input path for pickled feature mapping provided")


    def read_csv_data_dict(self):
        with open(self.data_dict_csv_path, "r") as fin:
            reader = csv.DictReader(fin)
            for row in reader:
                if (row['DataTreatment'] == 'Code'):
                    self.code_cols[row['Name']] = (row['DataTreatment'], row['DataType'], row['Temporal'], row['OneHotEncoded'])
                elif (row['DataTreatment'] == 'Numeric'):
                    self.numeric_cols.append(row['Name'])
                elif (row['DataTreatment'] == 'Combine'):
                    self.combine_cols.append(row['Name'])
                else:
                    self.drop_cols.append(row['Name'])        


    def get_code_mapping(self):
        with open(self.data_dict_pkl_path, "rb") as fin:
            code_d = pickle.load(fin)
        self.code_mappings = dict((v,k) for k,v in code_d.items())

    def load_categorical_dict(self):
        # read in precreated pickled data dictionary
        if self.categorical_feature_path:
            self.read_csv_categorical_dict(self.categorical_feature_path)
        else:
            logger.warning("No input path for csv categorical dictionary provided")


    def read_csv_categorical_dict(self, csv_path):
        # create dict for categorical features, {feature: n_total_levels}
        cat_name = {}
        with open(csv_path, "r") as fin:
            reader = csv.DictReader(fin)
            for row in reader:
                cat_name[row['Name']] = row['N']

        self.categorical_cols = cat_name

    def one_hot_encoding(self, feature):
        '''
        One-hot encoding, and rename categorical features
        :feature: dict {name: val}, e.g., {feature: 3}
        :categorical_feature_mapping: csv file with categorical features
        :return: new feature name, e.g., feature_3
        '''

        # create dict for categorical features, {feature: n_total_levels}
        cat_name = {}
        with open(self.categorical_feature_path, "r") as fin:
            reader = csv.DictReader(fin)
            for row in reader:
                cat_name[row['Name']] = row['N']

        (name, val), = feature.items()

        if cat_name.get(name):
            return '{}_{}'.format(name, val)

    def map_codes_to_ints(self):
        '''
        map one hot encoded features (binary) to integer feature names
        dump it to a pickle file
        "param outpath: data_dict_pkl_path
        :return: pickle file with one hot encoded features,
             e,g, {1: feature1, 2: feature2, ...}
        '''
        all_features = sorted(list(self.code_cols.keys()) + self.numeric_cols)
        with open(self.data_dict_pkl_path, "wb") as fin:
            pickle.dump(dict((i,all_features[i]) for i in range(len(all_features))), fin)


if __name__ == '__main__':
    config = dict()
    cd = os.path.dirname(os.path.realpath(__file__))
    for c in ['../config_default.json', '../config.json']:
        with open(os.path.join(cd, c), 'r') as fin:
            config.update(json.load(fin))
    # create the pickled integer feature mapping from categorical and data dictionary csv files
    data_dict_csv_path = os.path.realpath(config["DATA_DICTIONARY"]["data_dict_csv"])
    categorical_feature_path = os.path.realpath(config["DATA_DICTIONARY"]["categorical_feature"])
    data_dict_pkl_path = os.path.realpath(config["DATA_DICTIONARY"]["data_dict"])

    ddict = DataDictionary(data_dict_csv_path, data_dict_pkl_path, categorical_feature_path)
    ddict.create_data_dict()
