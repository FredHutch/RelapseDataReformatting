"""
create a data dictionary that maps distinct categorical or 'code' features
to unique integers for retain model training and interpretation
"""
import os
import csv
import pickle

class DataDictionary():
    def __init__(self, default_datadict=True, default_codes=True):
        self.code_cols = {}
        self.one_hot_encoded = {}
        self.numeric_cols = []
        self.drop_cols = []
        if default_datadict:
            self.read_data_dict(os.path.realpath('data_dict/data_dictionary.csv'))
        self.code_mappings = {}
        if default_codes:
            self.read_code_mapping(os.path.realpath('data_dict/data_dictionary.pkl'))

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



def map_codes_to_ints(filepath):
    '''
    map one hot encoded features (binary) to integer feature names
    dump it to a pickle file
    :param filepath: path of data_dictionary.csv
    :return: pickle file with one hot encoded features,
             e,g, {1: feature1, 2: feature2, ...}
    '''
    code_d = {}
    int_map_count = 1
    with open(filepath, "r") as fin:
        reader = csv.DictReader(fin)
        for row in reader:
            if (row['DataTreatment'] == 'Code'):
                code_d[int_map_count] = row['Name']
                int_map_count += 1
    with open(os.path.realpath('data_dict/data_dictionary.pkl'), 'wb') as code_map:
        pickle.dump(code_d, code_map)

def one_hot_encoding(categorical_features):
    '''
    To-do: one-hot encoding features while load in the data
    :param categorical_features:
    :return:
    '''
    # load categorical_features.csv
    # one hot encoding the features