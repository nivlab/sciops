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
subscales = ['mania', 'depression', 'anxiety', 'artistic', 'greed']

## Define permutation statistics (personal reliability).
n_iter = 1000

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### Load and prepare data.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

## Load metadata.
metadata = read_csv(os.path.join('data','metadata.csv'))

## Initialize metrics DataFrame.
metadata = metadata.query('prev_complete == 0 and bot == 0')
metrics = metadata[['platform','subject']].copy()

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

## Score infrequency items.
metrics['infreq_mania'] = np.where(surveys.mania_q08 < 3, 1, 0)
metrics['infreq_depression'] = np.where(surveys.depression_q08 > 0, 1, 0)
metrics['infreq_anxiety'] = np.where(surveys.anxiety_q08 > 0, 1, 0)
metrics['infreq_artistic'] = np.where(surveys.artistic_q07 != 3, 1, 0)
metrics['infreq_greed'] = np.where(surveys.greed_q07 < 4, 1, 0)

## Compute sum total.
metrics['infreq'] = metrics.filter(regex='infreq').sum(axis=1)

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
cols = ['platform','subject'] + [f'{scale}_rt' for scale in subscales]
rt = surveys[cols].copy()

## Iteratively compute scores.
for prefix in subscales:
    rt[f'{prefix}_rt'] /= surveys.filter(regex=f'{prefix}_q').columns.size

## Sum across items.
rt['survey_rt'] = rt.filter(regex='rt').sum(axis=1)

## Merge with reject.
metrics = metrics.merge(rt)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### 1.6 Key Variability.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
print('1.6 Computing key variability.')

## Compute most chosen option within subjects.
f = lambda x: np.abs(np.mean(x) - 0.5)
gb = data.groupby(['platform','subject']).state_1_key.apply(f).reset_index()

## Rename columns.
gb = gb.rename(columns={'state_1_key':'key_var'})

## Merge with reject.
metrics = metrics.merge(gb)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### 1.7 Choice Variability.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
print('1.7 Computing choice variability.')

## Compute most chosen option within subjects.
f = lambda x: np.abs(np.mean(x) - 0.5)
gb = data.groupby(['platform','subject']).state_1_choice.apply(f).reset_index()

## Rename columns.
gb = gb.rename(columns={'state_1_choice':'choice_var'})

## Merge with reject.
metrics = metrics.merge(gb)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### 1.8 Win-Stay Lose-Shift.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
print('1.8 Computing win-stay lose-shift.')

## Sort data.
data = data.sort_values(['platform','subject','state_2'])

## Define groupby object.
gb = data.groupby(['platform','subject','state_2'])

## Define trial-history regressors.
data['exposure'] = gb.trial.transform(lambda x: np.arange(x.size))
data['prev_choice'] = gb.state_2_choice.transform(np.roll, shift=1)
data['prev_outcome'] = gb.outcome.transform(np.roll, shift=1) - 0.5
data['stay'] = (data.state_2_choice == data.prev_choice).astype(int)
data['intercept'] = 1

## Mask first exposure.
data.loc[data.exposure == 0, ['prev_choice','prev_outcome','stay']] = np.nan
data = data.dropna()

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
f = lambda x: np.mean(x[['state_1_rt','state_2_rt']].values < 0.2)
gb = data.groupby(['platform','subject']).apply(f).reset_index()
gb = gb.rename(columns={0:'task_rt'})

## Merge with DataFrame.
metrics = metrics.merge(gb)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### Save data.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
print('Saving data.')

metrics.to_csv(os.path.join(DATA_DIR, 'metrics.csv'), index=False)