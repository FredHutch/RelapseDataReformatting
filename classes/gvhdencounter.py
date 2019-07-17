from operator import attrgetter
from classes.encounter import Encounter

class GVHDEncounter(Encounter):

    def __init__(self, df_row):
        date = df_row['date_gvhd']
        patientid = df_row['subject_id']
        days_since_epoch = df_row['days_hct1_gvhd']
        days_since_relapse = df_row['days_index_relapse_to_gvhd']
        super(GVHDEncounter, self).__init__(patientid, date, "GVHDEncounter")