import json
import os

from redcap import Project, RedcapError

def pull_from_red_cap(config):
	"""
	pull data from the Relapse REDCap project, load into dataframe
	*for now* output file to temporary csv
	"""
	URL = config["RED_CAP_ENGINE"]["URL"]
	API_KEY = config["RED_CAP_ENGINE"]["API"]
	project = Project(URL, API_KEY)

	try:
	    intermediate_df = project.export_records(format='df')
	except RedcapError:
	    print ("Failure to export records from REDCap")

	print (str(len(intermediate_df) )+ ' total records pulled')
	intermediate_df.to_csv(config['OUTPUT_FILEPATH'] + os.path.sep + 'intermediate_df.csv')
	

if __name__ == '__main__':
    with open('./config.json') as fin:
        config = json.load(fin)

    pull_from_red_cap(config)
