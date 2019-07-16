import json
import os
import pandas
import pandas_profiling

from redcap import Project, RedcapError

def pull_from_red_cap(config):
    """
    pull data from the Relapse REDCap project, load into dataframe
    *for now* output file to temporary csv
    """
    URL = config["RED_CAP_ENGINE"]["URL"]
    API_KEY = config["RED_CAP_ENGINE"]["API"]
    project = Project(URL, API_KEY)

    for form in project.forms:
        try:
            intermediate_df = project.export_records(forms=[form], format='df')
            intermediate_df = intermediate_df.loc[intermediate_df['redcap_repeat_instrument'].notnull()]
        except RedcapError:
            print ("Failure to export records from REDCap for form: {}".format(form))
            continue

        intermediate_df.isna().sum()
        length = intermediate_df.shape[0]
        print("Empty columns:")
        empty_cols = [col for col in list(intermediate_df) if intermediate_df[col].isna().sum() == length]
        print("length, width {}, number of empty columns: {}".format(intermediate_df.shape, len(empty_cols)))

        report = pandas_profiling.ProfileReport(intermediate_df)
        report.to_file(os.path.sep.join([config["OUTPUT_FILEPATH"], "{}.html".format(form)]))

if __name__ == '__main__':
    with open('./config.json') as fin:
        config = json.load(fin)

    pull_from_red_cap(config)
