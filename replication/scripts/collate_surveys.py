import os, json
import numpy as np
from os.path import dirname
from pandas import DataFrame, concat
ROOT_DIR = dirname(dirname(os.path.realpath(__file__)))
DATA_DIR = os.path.join(ROOT_DIR, 'data')
RAW_DIR = os.path.join(ROOT_DIR, 'raw')

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### Main loop.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

## Preallocate space.
METADATA = []
SURVEYS = []

## Iterate over platforms.
for platform in ['mturk', 'prolific']:

    ## Locate files.
    fdir = os.path.join(RAW_DIR, platform)
    files = sorted([f for f in os.listdir(fdir) if f.endswith('json')])

    for f in files:

        ## Load file.
        subject = f.replace('.json','')

        with open(os.path.join(fdir, f), 'r') as f:
            JSON = json.load(f)

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        ### Assemble metadata.
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

        ## Initialize dictionary.
        dd = dict(
            platform = platform,
            subject = subject, 
            total = np.round(JSON[-1]['time_elapsed'] * 1e-3 / 60, 2),
            interactions = len(eval(JSON[-1]['interactions']))
        )

        ## Demographics
        DEMO = [dd for dd in JSON if dd['trial_type'] == 'survey-demo']
        if DEMO: dd.update(DEMO[0]['responses'])

        ## Append.
        METADATA.append(dd)

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        ### Assemble survey data.
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

        ## Initialize dictionary.
        dd = dict(platform = platform, subject=subject)

        ## Gather surveys.
        templates = [dd for dd in JSON if dd['trial_type'] == 'survey-template']

        for prefix in ['mania', 'depression', 'anxiety', 'artistic', 'greed']:

            ## Extract survey.
            survey = [d for d in templates if prefix in d.get('survey', d['trial_type'])]
            if survey: survey, = survey
            else: continue

            ## Update dictionary.
            dd[f'{prefix}_rt'] = np.copy(np.round(survey['rt'] * 1e-3, 3))
            dd[f'{prefix}_radio'] = len(survey['radio_events'])
            dd[f'{prefix}_key'] = len(survey['key_events'])
            dd[f'{prefix}_mouse'] = len(survey['mouse_events'])
            dd[f'{prefix}_ipi'] = np.round(np.median(np.diff(survey['radio_events']) * 1e-3), 3)
            dd[f'{prefix}_infreq'] = survey.get('infrequency', np.nan)
            dd[f'{prefix}_sl'] = np.round(survey['straightlining'], 3)
            dd[f'{prefix}_zz'] = np.round(survey['zigzagging'], 3)
            dd[f'{prefix}_bot'] = survey['honeypot']

            ## Reformat responses.
            survey = {f'{prefix}_{k.lower()}': int(survey['responses'][k]) for k in sorted(survey['responses'])}

            ## Update dictionary.
            dd.update(survey)

        ## Append.
        SURVEYS.append(dd)
    
## Concatenate data.
SURVEYS = DataFrame(SURVEYS).sort_values(['platform','subject'])
METADATA = DataFrame(METADATA).sort_values(['platform','subject'])

## Include summary data.
SURVEYS.insert(2, 'infreq', SURVEYS.filter(regex='infreq').sum(axis=1))
SURVEYS.insert(3, 'straightlining', SURVEYS.filter(regex='sl').mean(axis=1).round(3))
SURVEYS.insert(4, 'zigzagging', SURVEYS.filter(regex='zz').mean(axis=1).round(3))
SURVEYS.insert(5, 'ipi', SURVEYS.filter(regex='ipi').mean(axis=1).round(3))
SURVEYS.insert(6, 'bot', SURVEYS.filter(regex='bot').sum(axis=1))

## Save.
SURVEYS.to_csv(os.path.join(DATA_DIR, 'surveys.csv'), index=False)
METADATA.to_csv(os.path.join(DATA_DIR, 'metadata.csv'), index=False)