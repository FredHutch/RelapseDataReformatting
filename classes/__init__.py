import itertools
import logging

from classes.event import gvhdencounter, relapseencounter, treatmentencounter, \
                          vitalsencounter, demographicsencounter, ispencounter, \
                          graftrejectionencounter, gatewayencounter

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# unimplemented instrument types commented out below
INSTRUMENT_TO_FACTORY_MAP = {'treatment_event': treatmentencounter.TreatmentEncounterFactory,
                             'gvhd': gvhdencounter.GVHDEncounterFactory,
                             'vital_status': vitalsencounter.VitalsEncounterFactory,
                             'response_or_relapse_event': relapseencounter.RelapseEncounterFactory,
                             'patient_id': demographicsencounter.DemographicsEncounterFactory,
                             'immunosuppression_kinetics': ispencounter.ISPEncounterFactory,
                             'graft_rejection':graftrejectionencounter.GraftRejectionEncounterFactory,
                             'gateway_encounter': gatewayencounter.gatewayEncounterFactory
                             # primary_prophylaxis_against_relapse ?
                             # prehct1_treatment ?
                             }

REPEAT_FORMS = {'treatment_event',
                'gvhd',
                'response_or_relapse_event',
                'immunosuppression_kinetics',
                'graft_rejection',
                # gateway ??
                # primary_prophylaxis_against_relapse ?
                # prehct1_treatment ?
                }


def map_instrument_df_to_class(instrument_name, instrument_df):
    # pass off single dataframe rows as Series to appropriate instrument factory
    # get back dictionary of event features, return list of event dictionaries
    if instrument_name in INSTRUMENT_TO_FACTORY_MAP.keys():
        event_list = []
        df = instrument_df
        enc_fact = INSTRUMENT_TO_FACTORY_MAP[instrument_name]()
        if instrument_name in REPEAT_FORMS:
            df = instrument_df.loc[instrument_df['redcap_repeat_instrument'].notnull()]
        for index, df_row in df.iterrows():
            event_list.append(enc_fact.make_encounters(index, df_row))
        event_list = list(itertools.chain(*[e for e in event_list]))
        return event_list
    else:
        warning_str = "no valid instrument types passed to mapper: {}".format(instrument_name)
        logger.warning(warning_str)
        return []



