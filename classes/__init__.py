import logging

from classes.event import gvhdencounter, relapseencounter, treatmentencounter, vitalsencounter, demographicsencounter

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# unimplemented instrument types commented out below
INSTRUMENT_TO_FACTORY_MAP = {'treatment_event': treatmentencounter.TreatmentEncounterFactory,
                             'gvhd': gvhdencounter.GVHDEncounterFactory,
                             'vital_status':vitalsencounter.VitalsEncounterFactory,
                             'response_or_relapse_event': relapseencounter.RelapseEncounterFactory,
                             'patient_id': demographicsencounter.DemographicsEncounterFactory,
                             # immunosuppression_kinetics ?
                             # primary_prophylaxis_against_relapse ?
                             # immunosuppression_kinetics ?
                             # prehct1_treatment ?
                             # graft_rejection ?
                             }

def map_instrument_df_to_class(instrument_name, instrument_df):
    # pass off single dataframe rows as Series to appropriate instrument factory
    # get back dictionary of event features, return list of event dictionaries
    if instrument_name in INSTRUMENT_TO_FACTORY_MAP.keys():
        event_list = []
        enc_fact = INSTRUMENT_TO_FACTORY_MAP[instrument_name]()
        for index, df_row in instrument_df.iterrows():            
            event_list.append(enc_fact.translate_df_to_dict(df_row))
        return event_list
    else:
        return []
        warning_str = "no valid instrument types passed to mapper: {}".format(instrument_name)
        logger.warning(warning_str)
        raise ValueError(warning_str)


