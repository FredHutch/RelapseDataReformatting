import logging
import datetime as dt
from logging.handlers import RotatingFileHandler


formatter = logging.Formatter(
        "%(asctime)s %(threadName)-11s %(levelname)-10s %(message)s")

streamhandler = logging.StreamHandler()
streamhandler.setLevel(logging.DEBUG)
streamhandler.setFormatter(formatter)

file_handler = RotatingFileHandler('RelapseDataFormatting_{}.log'.format(dt.datetime.now().date()),
                                   maxBytes=1024 * 1024 * 100, backupCount=20)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

logging.basicConfig(format=formatter, handlers=[file_handler, streamhandler], level=logging.INFO)

GATEWAY_FEATURE_RECODE_MAP = {'cmvx': {'-/-': 'neg_neg', '-/': 'neg_neg', '/': 'Unknown',
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

BUCKETS = {'txage':{0: (0, 1), 1: (1, 12), 2: (13, 18), 3: (18, 60), 4: (60, 160)},
           'relage':{0: (0, 1), 1: (1, 12), 2: (13, 18), 3: (18, 60), 4: (60, 160)},
           'pb_blasts':{0: (0, 1), 1:(1, 5), 2:(5, 20), 3:(20, 50), 4:(50, 100)},
           'bm_blasts':{0: (0, 1), 1:(1, 5), 2:(5, 20), 3:(20, 50), 4:(50, 100)},
           'wbc':{0: (0, .5), 1: (.5, 1), 2:(1, 10), 3: (10, 30), 4:(30, 50), 5: (50,100)}
           }