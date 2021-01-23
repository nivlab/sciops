import os
import numpy as np
from pandas import read_csv
from os.path import dirname, join
ROOT_DIR = dirname(dirname(os.path.realpath(__file__)))
DATA_DIR = os.path.join(ROOT_DIR, 'data')

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### Define parameters.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

## Define subscales. 
subscales = ['7u','7d','gad7','pswq','bis','bas','shaps']
minlengths = [4,4,4,4,4,4,4,5]

## Define permutation statistics (personal reliability).
n_iter = 1000

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### Load and prepare data.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

## Load metadata.
metadata = read_csv(os.path.join('data','metadata.csv'))

## Initialize metrics DataFrame.
metrics = metadata.loc[metadata['prev_complete']=="No",['platform','subject']].copy()

## Load survey data and restrict participants.
surveys = read_csv(os.path.join('data','surveys.csv'))
surveys = surveys.loc[surveys.subject.isin(metrics.subject)]

## Load items data and restrict participants.
items = read_csv(os.path.join('data','items.csv'))
items = items.loc[items.subject.isin(metrics.subject)]
items = items.drop(columns=['subject','platform'])

## Load task data and restrict participants.
data = read_csv(os.path.join('data','data.csv'))
data = data.loc[data.subject.isin(metrics.subject)]

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### 1.1 Infrequency Items.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
## Following Huang et al. (2015) and Ophir et al. (2019), we included 4 infrequency items in our surveys. 
## These are items with a correct or highly probable answer.
print('1.1 Computing infreqency metric.')

## Extract infrequency items.
cols = ['platform','subject','gad7_q08','7u7d_q15','bisbas_q13','shaps_q15']
infreq = surveys[cols].copy()
infreq.columns = ['platform','subject','infreq_gad7','infreq_7u7d','infreq_bisbas','infreq_shaps']

## Score infrequency items.
infreq['infreq_gad7'] = np.in1d(infreq['infreq_gad7'], (1,2,3)).astype(int)
infreq['infreq_7u7d'] = np.in1d(infreq['infreq_7u7d'], (1,2,3)).astype(int)
infreq['infreq_bisbas'] = np.in1d(infreq['infreq_bisbas'], (0,1)).astype(int)
infreq['infreq_shaps'] = np.in1d(infreq['infreq_shaps'], (0,1)).astype(int)

## Sum across items.
infreq['infreq'] = infreq.filter(regex='infreq').sum(axis=1)

## Merge with metrics.
metrics = metrics.merge(infreq)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### 1.2 Inter-item Standard Deviation.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
print('1.2 Computing inter-item standard deviation.')

## Preallocate space.
isd = np.zeros((len(items), len(subscales)))

## Iteratively compute ISD.
for i, subscale in enumerate(subscales):
    
    ## Extract responses.
    X = items.filter(regex=subscale).values.copy()

    ## Compute ISD.
    a = np.power(X - X.mean(axis=1)[:,np.newaxis], 2).sum(axis=1)
    b = X.shape[1] - 1
    isd[:,i] = np.sqrt(a / b)
    
## Sum across subscales.
isd = isd.sum(axis=1)

## Add to reject DataFrame.
metrics['isd'] = isd

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### 1.3 Personal reliability.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
print('1.3 Computing personal reliability.')
np.random.seed(47404)

## Main loop.
reliability = np.zeros((n_iter, len(items)), dtype=float)

for i in range(n_iter):
    
    ## Preallocate space.
    X = np.zeros((len(items), len(subscales)))
    Y = np.zeros((len(items), len(subscales)))
    
    ## Iteratively compute split-half scores.    
    for j, subscale in enumerate(subscales):
        
        ## Permute items in subscale.
        ix = np.random.permutation(items.filter(regex=subscale).columns)
        
        ## Compute average within each half.
        X[:,j] = items[ix[::2]].mean(axis=1)
        Y[:,j] = items[ix[1::2]].mean(axis=1)
        
    ## Compute correlation coefficient.
    a = np.mean(X * Y, axis=1) - np.mean(X, axis=1) * np.mean(Y, axis=1)
    b = np.std(X, axis=1) * np.std(Y, axis=1)
    reliability[i] = a / b
    
## Average across permutations.
reliability = reliability.mean(axis=0)

## Add to reject DataFrame.
metrics['reliability'] = reliability

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### 1.4 Mahalanobis D.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
print('1.4 Computing Mahalanobis D.')

## Compute (inverse) covariance matrix.
Sigma = items.cov()
Sigma_inv = np.linalg.inv(Sigma)

## Preallocate space.
mahalanobis = np.zeros(items.shape[0])

## Iteratively compute Mahalanobis D.
mu = items.mean()
for i in range(items.shape[0]):
    x = items.iloc[i] - mu
    mahalanobis[i] = np.sqrt(x @ Sigma_inv @ x)
        
## Add to reject DataFrame.
metrics['mahalanobis'] = mahalanobis

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### 1.5 Reading time.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
print('1.5 Computing reading times.')

## Extract response times.
rt = surveys[['platform','subject','gad7_rt','7u7d_rt','bisbas_rt','shaps_rt','pswq_rt']].copy()

## Iteratively compute scores.
for prefix in ['gad7','7u7d','bisbas','shaps','pswq']:
    rt[f'{prefix}_rt'] /= surveys.filter(regex=f'{prefix}_q').columns.size

## Sum across items.
rt['survey_rt'] = rt.filter(regex='rt').sum(axis=1)

## Merge with reject.
metrics = metrics.merge(rt)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### 1.6 Choice Variability.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
print('1.6 Computing choice variability.')

## Compute most chosen option within subjects.
gb = data.groupby(['platform','subject']).choice.apply(lambda x: x.value_counts().max() / x.size).reset_index()

## Rename columns.
gb = gb.rename(columns={'choice':'variability'})

## Merge with reject.
metrics = metrics.merge(gb)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### 1.7 Choice Accuracy.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
print('1.7 Computing choice accuracy.')

## Compute within-subject accuracy.
gb = data.groupby(['platform','subject']).accuracy.mean().reset_index()

## Merge with reject.
metrics = metrics.merge(gb)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### 1.8 Win-Stay Lose-Shift.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
print('1.8 Computing win-stay lose-shift.')

## Define previous outcome.
f = lambda x: np.where(np.roll(x, 1), 0.5, -0.5)
data['prev_outcome'] = data.groupby('subject').outcome.transform(f)
data.loc[data.trial==1,'prev_outcome'] = np.nan

## Define stay choices.
f = lambda x: (x == np.roll(x,1)).astype(int)
data['stay'] = data.groupby('subject').choice.transform(f)
data.loc[data.trial==1,'stay'] = np.nan

## Define intercept.
data['intercept'] = 1

## Compute pivot table.
pivot = data.groupby(['platform','subject','prev_outcome']).stay.mean().reset_index()
pivot = pivot.pivot_table('stay',['platform','subject'],'prev_outcome').reset_index()

## Define WSLS regression.
def wsls_regression(df):
    df = df.dropna().copy()
    X = df[['intercept','prev_outcome']].dropna().values    
    y = df['stay']
    return np.linalg.lstsq(X,y,rcond=-1)[0][-1]

## Compute WSLS coefficient.
gb = data.groupby(['platform','subject']).apply(wsls_regression).reset_index()
gb = gb.rename(columns={0:'wsls'})

## Merge with reject.
metrics = metrics.merge(gb)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### 1.9 Response times.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
print('1.9 Computing response time outliers.')

## Compute within-subject response time flags.
gb = data.groupby(['platform','subject']).rt.apply(lambda x: np.mean(x < 0.2)).reset_index()
gb = gb.rename(columns={'rt':'task_rt'})

## Merge with DataFrame.
metrics = metrics.merge(gb)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### Save data.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
print('Saving data.')

metrics.to_csv(os.path.join(DATA_DIR, 'metrics.csv'), index=False)