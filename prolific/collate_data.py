import os, json
import numpy as np
from os.path import dirname
from pandas import DataFrame, concat
ROOT_DIR = dirname(os.path.realpath(__file__))
DATA_DIR = os.path.join(ROOT_DIR, 'data')
RAW_DIR = os.path.join(ROOT_DIR, 'raw')

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### Main loop.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

## Locate files.
files = sorted([f for f in os.listdir(RAW_DIR) if f.endswith('json')])

## Preallocate space.
METADATA = []
SURVEYS = []
DATA = []

for f in files:
    
    ## Load file.
    subject, = f.replace('.json','').split('_')
    
    with open(os.path.join(RAW_DIR, f), 'r') as f:
        JSON = json.load(f)
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    ### Assemble behavioral data.
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    
    ## Assemble behavioral data.
    data = DataFrame([dd for dd in JSON if dd['trial_type'] == 'three-arm-trial'])
    n_missing = data.missing.sum()
    data = data.query('missing==False')
        
    ## Error-catching: exclude incomplete datasets.
    if data.shape[0] < 90: 
        print(f'Skipping {subject}')
        continue
        
    ## Define columns of interest.
    cols = ['trial','correct','choice','key','rt','accuracy','outcome']
    
    ## Limit to columns of interest.
    data = data[cols]
    
    ## Reformat columns.
    data['rt'] = np.where(data['rt'] < 0, np.nan, data['rt'] * 1e-3).round(3)
    
    ## Insert subject ID. Append.
    data.insert(0,'subject',subject)
    DATA.append(data)    
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    ### Assemble metadata.
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    
    ## Gather surveys.
    demo, = [dd for dd in JSON if dd['trial_type'] == 'survey-demo']
    comp = len([dd for dd in JSON if dd['trial_type'] == 'three-arm-comprehension'])
    
    ## Initialize dictionary.
    time_elapsed = np.round(JSON[-1]['time_elapsed'] / 1000. / 60., 1)
    dd = dict(subject=subject, minutes=time_elapsed, n_loops=comp, missing=n_missing)
    
    ## Insert demographic variables.
    for k,v in demo['responses'].items(): dd[k] = v
    
    ## Append.
    METADATA.append(dd)
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    ### Assemble survey data.
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        
    ## Initialize dictionary.
    dd = dict(subject=subject)
    
    ## Gather surveys.
    templates = [dd for dd in JSON if dd['trial_type'] == 'survey-template']
    
    for prefix in ['gad7','7up7down','bisbas','pswq','shaps']:
        
        ## Extract survey.
        survey = [d for d in templates if d['survey']==prefix]
        if survey: survey, = survey
        else: continue
        
        ## Format prefix.
        if prefix == '7up7down': prefix = '7u7d'
        
        ## Get RT.
        rt = np.copy(np.round(survey['rt'] * 1e-3, 3))
        
        ## Reformat responses.
        survey = {f'{prefix}-{k}'.lower(): survey['responses'][k] for k in sorted(survey['responses'])}
    
        ## Update dictionary.
        dd.update(survey)
        dd[f'{prefix}-rt'] = rt

    ## Append.
    SURVEYS.append(dd)
    
## Concatenate data.
DATA = concat(DATA).sort_values(['subject','trial'])
SURVEYS = DataFrame(SURVEYS).sort_values(['subject'])
METADATA = DataFrame(METADATA).sort_values(['subject'])

## Insert platform metadata.
DATA.insert(0, 'platform', 'prolific')
SURVEYS.insert(0, 'platform', 'prolific')
METADATA.insert(0, 'platform', 'prolific')

## Save.
DATA.to_csv(os.path.join(DATA_DIR, 'data.csv'), index=False)
SURVEYS.to_csv(os.path.join(DATA_DIR, 'surveys.csv'), index=False)
METADATA.to_csv(os.path.join(DATA_DIR, 'metadata.csv'), index=False)
print(f'N = {METADATA.shape[0]}')
