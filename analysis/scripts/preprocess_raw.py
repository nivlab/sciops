import os, json
import numpy as np
from os.path import dirname, join
from pandas import DataFrame, concat
ROOT_DIR = dirname(dirname(os.path.realpath(__file__)))
DATA_DIR = os.path.join(ROOT_DIR, 'data')
MTURK_DIR = os.path.join(ROOT_DIR, 'raw', 'mturk')
PROLIFIC_DIR = os.path.join(ROOT_DIR, 'raw', 'prolific')

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### Main loop.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

## Preallocate space.
METADATA = []
SURVEYS = []
DATA = []

## Locate files.
files = [os.path.join(MTURK_DIR,f) for f in os.listdir(MTURK_DIR) if f.endswith('json')] +\
        [os.path.join(PROLIFIC_DIR,f) for f in os.listdir(PROLIFIC_DIR) if f.endswith('json')]
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
        survey = {f'{prefix}_{k}'.lower(): survey['responses'][k] for k in sorted(survey['responses'])}
    
        ## Update dictionary.
        dd.update(survey)
        dd[f'{prefix}_rt'] = rt

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

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### Preprocess data.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

## Update overlapping columns.
METADATA.insert(11, 'other_platform', np.where(METADATA['prolific'].isnull(), METADATA['mturk'], METADATA['prolific']))
METADATA.insert(12, 'prev_complete', np.where(METADATA['prolific-this-study'].isnull(), METADATA['mturk-this-study'], METADATA['prolific-this-study']))
METADATA = METADATA.drop(columns=['prolific','prolific-this-study','mturk','mturk-this-study'])

## Update BIS/BAS (reverse scoring: strongly disagree = 0, strongly agree = 3).
## https://local.psy.miami.edu/people/faculty/ccarver/availbale-self-report-instruments/bisbas-scales
cols = ['bisbas_q01','bisbas_q02','bisbas_q03','bisbas_q04',
        'bisbas_q05','bisbas_q06','bisbas_q07','bisbas_q08',
        'bisbas_q09','bisbas_q10','bisbas_q11','bisbas_q12']
SURVEYS[cols] = (3 - SURVEYS[cols].astype(int)) + 1

## Update SHAPS (reverse scoring: strongly disagree = 0, strongly agree = 3).
## https://datashare.nida.nih.gov/instrument/snaith-hamilton-pleasure-scale
cols = ['shaps_q01','shaps_q02','shaps_q03','shaps_q04','shaps_q05',
        'shaps_q06','shaps_q07','shaps_q08','shaps_q09','shaps_q10',
        'shaps_q11','shaps_q12','shaps_q13','shaps_q14']
SURVEYS[cols] = 3 - SURVEYS[cols].astype(int)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### Assemble subscales.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

## Define subscales.
subscales = {
    '7u':    ['7u7d_q01','7u7d_q03','7u7d_q04','7u7d_q06','7u7d_q07','7u7d_q08','7u7d_q13'],
    '7d':    ['7u7d_q02','7u7d_q05','7u7d_q09','7u7d_q10','7u7d_q11','7u7d_q12','7u7d_q14'],
    'gad7':  ['gad7_q01','gad7_q02','gad7_q03','gad7_q04','gad7_q05','gad7_q06','gad7_q07'],
    'pswq':  ['pswq_q01','pswq_q02','pswq_q03'],
    'bis':   ['bisbas_q01','bisbas_q02','bisbas_q03','bisbas_q04'],
    'bas_r': ['bisbas_q05','bisbas_q06','bisbas_q07','bisbas_q08'],
    'bas_d': ['bisbas_q09','bisbas_q10','bisbas_q11','bisbas_q12'],
    'shaps': ['shaps_q01','shaps_q02','shaps_q03','shaps_q04','shaps_q05',
              'shaps_q06','shaps_q07','shaps_q08','shaps_q09','shaps_q10',
              'shaps_q11','shaps_q12','shaps_q13','shaps_q14'],
}

## Assemble items.
ITEMS = np.append(['platform','subject'], np.concatenate(list(subscales.values())))
ITEMS = SURVEYS[ITEMS]

## Update columns.
rename = {v:'_'.join([k, v.split('_')[-1]]) for k, v in subscales.items() for v in v}
ITEMS = ITEMS.rename(columns=rename)

## Compute sum scores.
SCORES = ITEMS.copy()
for k in subscales.keys(): SCORES[k] = SCORES.filter(regex=k).astype(int).sum(axis=1)
SCORES = SCORES[np.append(['platform','subject'], list(subscales.keys()))]

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### Save data.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

METADATA.to_csv(os.path.join(DATA_DIR, 'metadata.csv'), index=False)
SURVEYS.to_csv(os.path.join(DATA_DIR, 'surveys.csv'), index=False)
ITEMS.to_csv(os.path.join(DATA_DIR, 'items.csv'), index=False)
SCORES.to_csv(os.path.join(DATA_DIR, 'scores.csv'), index=False)
DATA.to_csv(os.path.join(DATA_DIR , 'data.csv'), index=False)
