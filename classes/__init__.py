import logging

from classes.event import gvhdencounter, relapseencounter, treatmentencounter, vitalsencounter, demographicsencounter

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

INSTRUMENT_TO_FACTORY_MAP = {'treatment_event': treatmentencounter.TreatmentEncounter,
                             'gvhd': gvhdencounter.GVHDEncounter,
                             'vital_status':vitalsencounter.VitalsEncounter,
                             'response_or_relapse_event': relapseencounter.RelapseEncounter,
                             'patient_id': demographicsencounter.DemographicsEncounter,
                             }


def map_instrument_df_to_class(instrument_df):
    instrument = instrument_df['redcap_repeat_instrument'].unique()

    # multiple instruments passed at once. raise error.
    if len(instrument) > 1:
        warning_str = "multiple instrument types passed to mapper within single df: {}".format(instrument)
        logger.warning(warning_str)
        raise ValueError(warning_str)
    # one of the non-repeating forms.
    else:
        if instrument in INSTRUMENT_TO_FACTORY_MAP.keys():
            return INSTRUMENT_TO_FACTORY_MAP[instrument]
        # Vital Status
        elif 'vital_status_complete' in instrument_df:
            return INSTRUMENT_TO_FACTORY_MAP['vital_status']
        elif 'patient_id_complete' in instrument_df:
            return INSTRUMENT_TO_FACTORY_MAP['patient_id']
        else:
            warning_str = "no valid instrument types passed to mapper: {}".format(instrument)
            logger.warning(warning_str)
            raise ValueError(warning_str)


