import os, json
import numpy as np
from os.path import dirname, join
from pandas import DataFrame, concat, read_csv
from tqdm import tqdm
ROOT_DIR = dirname(dirname(os.path.realpath(__file__)))
DATA_DIR = os.path.join(ROOT_DIR, 'data')
RAW_DIR = os.path.join(ROOT_DIR, 'raw')

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### Main loop.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

## Preallocate space.
data = []

## Iterate over platforms.
for platform in ['mturk', 'prolific']:

    ## Locate files.
    fdir = os.path.join(RAW_DIR, platform)
    files = sorted([f for f in os.listdir(fdir) if f.endswith('json')])

    for f in files:

        ## Define subject
        subject = f.replace('.json','')

        ## Load JSON.
        with open(os.path.join(fdir, f), 'r') as tmp:
            JSON = json.load(tmp)

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        ### Assemble data.
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

        ## Extract two-step task.
        df = [dd for dd in JSON if dd['trial_type'] == 'two-step-trial']
        df = DataFrame(df).query('trial > 0 and missing == False')

        ## Reduce to columns of interest.
        cols = ['trial','drift_ix','state_1_key','state_1_choice','state_1_rt',
                'transition','state','state_2_key','state_2_choice','state_2_rt','outcome',
                'minimum_resolution','browser_interactions']
        df = df[cols]

        ## Format columns.
        df['state_1_rt'] = np.round(df['state_1_rt'] * 1e-3, 3)
        df['state_2_rt'] = np.round(df['state_2_rt'] * 1e-3, 3)
        df = df.rename(columns={'state':'state_2'})
        df.insert(0, 'subject', subject)
        df.insert(0, 'platform', platform)

        ## Append.
        data.append(df)
    
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### Save data.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

## Concatenate data.
data = concat(data).sort_values(['platform','subject','trial'])

## Save data.
data.to_csv(os.path.join(DATA_DIR , 'data.csv'), index=False)