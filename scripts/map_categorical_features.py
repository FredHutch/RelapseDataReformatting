"""
create a data dictionary that maps distinct categorical or 'code' features
to unique integers for retain model training and interpretation
"""

import csv
import pickle

class DataDictionary():
    def __init__(self, default_datadict=True, default_codes=True):
        self.code_cols = {}
        self.one_hot_encoded = {}
        self.numeric_cols = []
        self.drop_cols = []
        if default_datadict:
            self.read_data_dict('./data_dictionary.csv')
        self.code_mappings = {}
        if default_codes:
            self.read_code_mapping('./dictionary.pkl')

    def read_data_dict(self, filepath):
        with open(filepath, "r") as fin:
            reader = csv.DictReader(fin)
            for row in reader:
                if (row['DataTreatment'] == 'Code' and row['OneHotEncoded'] == 'Yes'):
                    self.one_hot_encoded[row['Name']] = (row['DataTreatment'], row['DataType'], row['Temporal'], row['OneHotEncoded'])
                elif (row['DataTreatment'] == 'Code' and row['OneHotEncoded'] == 'No'):
                    self.code_cols[row['Name']] = (row['DataTreatment'], row['DataType'], row['Temporal'], row['OneHotEncoded'])
                elif (row['DataTreatment'] == 'Numeric'):
                    self.numeric_cols.append(row['Name'])
                else:
                    self.drop_cols.append(row['Name'])

    def read_code_mapping(self, filepath):
        with open(filepath, "rb") as fin:
            code_map = pickle.load(fin)
        self.code_mappings = {v:k for k,v in code_map.items()}


## to-do map code and save dict to a pickle
