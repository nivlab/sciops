import os, json
import numpy as np
from os.path import dirname, join
from pandas import DataFrame, concat
ROOT_DIR = dirname(os.path.realpath(__file__))
MTURK_DIR = os.path.join(ROOT_DIR, 'mturk')
PROLIFIC_DIR = os.path.join(ROOT_DIR, 'prolific')

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### Main loop.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

## Preallocate space.
METADATA = []
SURVEYS = []
DATA = []

## Locate files.
files = [os.path.join(ROOT_DIR,'mturk',f) for f in os.listdir(join(ROOT_DIR, 'mturk')) if f.endswith('json')] +\
        [os.path.join(ROOT_DIR,'prolific',f) for f in os.listdir(join(ROOT_DIR, 'prolific')) if f.endswith('json')]
files = sorted(files)

for f in files:
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    ### Load JSON file.
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    
    ## Load file.
    platform, subject = f.split(os.sep)[-2:]
    subject = subject.replace('.json','')
    
    with open(f, 'r') as f:
        JSON = json.load(f)
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    ### Assemble metadata.
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    
    ## Error-catching: exclude incomplete datasets.
    try: 
        demo, = [dd for dd in JSON if dd['trial_type'] == 'survey-demo']
        comp = len([dd for dd in JSON if dd['trial_type'] == 'three-arm-comprehension'])
    except ValueError:
        print(f'Skipping {platform} {subject}')
        continue
    
    ## Initialize dictionary.
    total_time = np.round(JSON[-1]['time_elapsed'] * 1e-3, 0)
    interactions = len(eval(JSON[-1]['interactions']))
    dd = dict(platform=platform, subject=subject, total_time=total_time, interactions=interactions)
    
    ## Insert demographic variables.
    for k,v in demo['responses'].items(): dd[k] = v
    dd['n_loops'] = comp
    
    ## Append.
    METADATA.append(dd)
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    ### Assemble survey data.
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        
    ## Initialize dictionary.
    dd = dict(platform=platform, subject=subject)
    
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
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    ### Assemble behavioral data.
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    
    ## Assemble behavioral data.
    data = DataFrame([dd for dd in JSON if dd['trial_type'] == 'three-arm-trial'])
    data = data.query('missing==False')
        
    ## Define columns of interest.
    cols = ['trial','correct','choice','key','rt','accuracy','outcome']
    
    ## Limit to columns of interest.
    data = data[cols]
    
    ## Reformat columns.
    data['rt'] = np.where(data['rt'] < 0, np.nan, data['rt'] * 1e-3).round(3)
    
    ## Insert subject ID. Append.
    data.insert(0,'platform',platform)
    data.insert(1,'subject',subject)
    data.insert(2,'block',(data.trial-1)//15+1)
    DATA.append(data)    
    
## Concatenate data.
METADATA = DataFrame(METADATA).sort_values(['platform','subject'])
SURVEYS = DataFrame(SURVEYS).sort_values(['platform','subject'])
DATA = concat(DATA).sort_values(['platform','subject','trial'])

## Update non-overlapping columns.
METADATA.insert(11, 'other-platform', np.where(METADATA['prolific'].isnull(), METADATA['mturk'], METADATA['prolific']))
METADATA.insert(12, 'prev-complete', np.where(METADATA['prolific-this-study'].isnull(), METADATA['mturk-this-study'], METADATA['prolific-this-study']))
METADATA = METADATA.drop(columns=['prolific','prolific-this-study','mturk','mturk-this-study'])

## Update BIS/Bas.
cols = ['bisbas-q01','bisbas-q02','bisbas-q03','bisbas-q04',
        'bisbas-q05','bisbas-q06','bisbas-q07','bisbas-q08',
        'bisbas-q09','bisbas-q10','bisbas-q11','bisbas-q12']
SURVEYS[cols] = (3 - SURVEYS[cols].astype(int)) + 1

## Update SHAPS.
cols = ['shaps-q01','shaps-q02','shaps-q03','shaps-q04','shaps-q05',
        'shaps-q06','shaps-q07','shaps-q08','shaps-q09','shaps-q10',
        'shaps-q11','shaps-q12','shaps-q13','shaps-q14']
SURVEYS[cols] = 3 - SURVEYS[cols].astype(int)

## Save.
METADATA.to_csv(os.path.join(ROOT_DIR, 'metadata.csv'), index=False)
SURVEYS.to_csv(os.path.join(ROOT_DIR, 'surveys.csv'), index=False)
DATA.to_csv(os.path.join(ROOT_DIR, 'data.csv'), index=False)
