import os
import numpy as np
from pandas import DataFrame, read_csv
from os.path import dirname, join
ROOT_DIR = dirname(dirname(os.path.realpath(__file__)))
DATA_DIR = os.path.join(ROOT_DIR, 'data')
STAN_DIR = os.path.join(ROOT_DIR, 'stan_results')

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### Load and prepare data.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

## Load metadata and restrict participants.
metadata = read_csv(os.path.join('data','metadata.csv'))
metadata = metadata.loc[metadata['prev_complete']=="No",['platform','subject']].copy()

## Load task data and restrict participants.
data = read_csv(os.path.join('data','data.csv'))
data = data.loc[data.subject.isin(metadata.subject)]

## Initialize correlates DataFrame.
corr = metadata[['platform','subject']].copy()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### 1.1 Accuracy.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
print('1.1 Computing accuracy.')

## Compute accuracy.
gb = data.groupby(['platform','subject']).accuracy.mean().reset_index()

## Merge with correlates.
corr = corr.merge(gb)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### 1.2 Total Points.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
print('1.2 Computing points total.')

## Compute points.
gb = data.groupby(['platform','subject']).outcome.sum().reset_index()
gb = gb.rename(columns={'outcome':'points'})

## Merge with correlates.
corr = corr.merge(gb)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### 1.3 Win-Stay Rates.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
print('1.3 Computing win-stay rates.')

## Determine previous win trials.
f = lambda x: np.roll(x, 1)
data['prev_win'] = data.groupby(['platform','subject']).outcome.transform(f)
data.loc[data.trial==1, 'prev_win'] = np.nan

## Determine stay trials.
f = lambda x: (x == np.roll(x,1)).astype(int)
data['stay'] = data.groupby(['platform','subject']).choice.transform(f)
data.loc[data.trial==1, 'stay'] = np.nan

## Compute win-stay rate.
gb = data.query('prev_win==1').groupby(['platform','subject']).stay.mean().reset_index()
gb = gb.rename(columns={'stay':'ws'})

## Merge with correlates.
corr = corr.merge(gb)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### 1.4 Lose-Shift Rates.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
print('1.4 Computing lose-shift rates.')

## Compute lose-shift rate.
gb = data.query('prev_win==0').groupby(['platform','subject']).stay.mean().reset_index()
gb = gb.rename(columns={'stay':'ls'})
gb['ls'] = 1 - gb['ls']

## Merge with correlates.
corr = corr.merge(gb)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### 1.5 Perseveration Errors.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
print('1.5 Computing perseveration errors.')

## Define trial number within each block.
data['exposure'] = data.groupby(['subject','block']).trial.transform(lambda x: np.arange(x.size)+1)

## Define perseveration errors.
data['perseveration'] = data.groupby('subject').correct.transform(lambda x: np.roll(x, 15))
data['perseveration'] = (data['perseveration'] == data['choice']).astype(int)
data.loc[data.block==1,'perseveration'] = np.nan

## Compute perseveration errors within participants.
gb = data.groupby(['platform','subject']).perseveration.mean().reset_index()

## Merge with correlates.
corr = corr.merge(gb)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### 1.6 Model-based correlates. 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
print('1.6 Extracting Stan parameters.')

## Load StanFit.
df = read_csv('stan_results/rstd.tsv.gz', sep='\t', compression='gzip')

## Extract parameters of interest.
beta  = df.filter(regex='beta').median().values
eta_p = df.filter(regex='^eta_p').median().values
eta_n = df.filter(regex='^eta_n').median().values
kappa = (eta_p - eta_n) / (eta_p + eta_n)

## Convert to DataFrame.
params = DataFrame(np.column_stack([beta,eta_p,eta_n,kappa]),
                   columns=['beta','eta_p','eta_n','kappa'])

## Append metadata.
params['platform'] = corr.sort_values('subject').platform.values
params['subject']  = corr.sort_values('subject').subject.values

## Merge with correlates.
corr = corr.merge(params)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### Save data.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
print('Saving data.')

corr.to_csv(os.path.join(DATA_DIR, 'correlates.csv'), index=False)