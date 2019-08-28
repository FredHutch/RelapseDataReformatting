"""
create a data dictionary that maps distinct categorical or 'code' features
to unique integers for retain model training and interpretation
"""
import os
import csv
import pickle

gateway_feature_recode_map = {'cmvx': {'-/-': 'neg_neg', '-/': 'neg_neg', '/': 'Unknown',
                                       '+/-': 'Others', '+/+': 'Others', '-/+': 'Others',
                                       '+/': 'Others', '-/+': 'Others',
                                       # equivocal is considered as +
                                       'equivocal/unknown': 'Unknown', 'equivocal/-': 'Other'},
                              'tbidose': {'0': 'le450', '200': 'le450', '300': 'le450', '450': 'le450',
                                          '1200': 'ge1200', '1320': 'ge1200'},
                              'proplbl': {
                                  # contains full list of the proplbl
                                  'FK506': 'CNI',
                                  'NEORAL': 'CNI',
                                  'CSP': 'CNI',
                                  'CYCLOSPORINE': 'CNI',
                                  'CSA': 'CNI',
                                  'TACROLIMUS' : 'CNI',
                                  'RAPA': 'RAPA',
                                  'SIROLIUMS': 'RAPA',
                                  'MMF': 'MMF',
                                  '[MYCOPHENOLATESODIUM]': 'MMF',
                                  'CY': 'Post-Transplant_Cyclophosphamide',
                                  'PTCY': 'Post-Transplant_Cyclophosphamide',
                                  'STEROIDS': 'STEROIDS', # ignore STEROIDS
                                  'MTX': 'MTX'
                              },
                              'hla_cco': {'ISO/MATCHED': 'REL/MATCHED',
                                          'REL/MATCHED': 'REL/MATCHED',
                                          'REL/MISMATCH': 'REL/MISMATCH',
                                          'REL/HAPLOIDENTICAL': 'REL/HAPLOIDENTICAL',
                                          'REL/UNKNOWN': '',
                                          'RD/CORD': 'CORD',
                                          'URD/CORD-COMBINED': 'CORD',
                                          'URD/MATCHED': 'URD/MATCHED',
                                          'URD/MISMATCH': 'URD/MISMATCH'}}


class DataDictionary():

    def __init__(self, data_dict_csv_path, data_dict_pkl_path, categorical_feature_path):
        self.code_cols = {}
        self.numeric_cols = []
        self.drop_cols = []
        self.code_mappings = {}
        self.categorical_feature_path = categorical_feature_path
        self.read_data_dict(data_dict_csv_path)
        self.read_code_mapping(data_dict_pkl_path)

    def read_data_dict(self, filepath):
        with open(filepath, "r") as fin:
            reader = csv.DictReader(fin)
            for row in reader:
                if (row['DataTreatment'] == 'Code'):
                    self.code_cols[row['Name']] = (row['DataTreatment'], row['DataType'], row['Temporal'], row['OneHotEncoded'])
                elif (row['DataTreatment'] == 'Numeric'):
                    self.numeric_cols.append(row['Name'])
                else:
                    self.drop_cols.append(row['Name'])

    def read_code_mapping(self, filepath):
        with open(filepath, "rb") as fin:
            code_map = pickle.load(fin)
        self.code_mappings = {v:k for k,v in code_map.items()}

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

def map_codes_to_ints(datadict, outpath):
    '''
    map one hot encoded features (binary) to integer feature names
    dump it to a pickle file
    :param datadict: data_dict_csv_path
    "param outpath: data_dict_pkl_path
    :return: pickle file with one hot encoded features,
             e,g, {1: feature1, 2: feature2, ...}
    '''
    code_d = {}
    int_map_count = 1
    with open(datadict, "r") as fin:
        reader = csv.DictReader(fin)
        for row in reader:
            if (row['DataTreatment'] == 'Code'):
                code_d[int_map_count] = row['Name']
                int_map_count += 1
    with open(outpath, 'wb') as code_map:
        pickle.dump(code_d, code_map)


