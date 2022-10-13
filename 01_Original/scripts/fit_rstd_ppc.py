import os
import numpy as np
from numba import njit
from os.path import dirname
from pandas import DataFrame, read_csv
from tqdm import tqdm
ROOT_DIR = dirname(dirname(os.path.realpath(__file__)))

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### Load and prepare data.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

## Load data.
data = read_csv(os.path.join('data', 'data.csv'))

## Restrict participants.
metrics = read_csv(os.path.join('data', 'metrics.csv'))
data = data[data.subject.isin(metrics.subject)].reset_index(drop=True)

## Load parameters.
params = read_csv(os.path.join('stan_results', 'rstd.tsv.gz'), sep='\t', compression='gzip')

## Reformat data.
data = data.sort_values(['subject','trial']).reset_index(drop=True)
metrics = metrics.sort_values('subject').reset_index(drop=True)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### Posterior predictive check.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
np.random.seed(47404)

@njit
def softmax(arr):
    """Scale-robust softmax function"""
    arr = np.exp(arr - np.max(arr))
    return arr / arr.sum()

def categorical_logit_rng(arr):
    return np.argmax(np.random.multinomial(1, softmax(arr)))

## Define metadata.
N = data.subject.nunique()
T = data.trial.nunique()

## Define data.
Y = data.pivot_table('choice','subject','trial').values.astype(int)
R = data.pivot_table('outcome','subject','trial').values.astype(int)
C = data.pivot_table('correct','subject','trial').values.astype(int)

## Preallocate space.
y_hat = np.zeros((N,T))
a_hat = np.zeros((N,T))

for i in tqdm(range(N)):
    
    ## Extract parameters.
    beta  = params.filter(regex=f'beta\[{i+1}\]').values.squeeze()
    eta_p = params.filter(regex=f'eta_p\[{i+1}\]').values.squeeze()
    eta_n = params.filter(regex=f'eta_n\[{i+1}\]').values.squeeze()
    
    ## Initialize Q-values.
    Q = 0.5 * np.ones((3,beta.size))
    
    for j in range(T):
        
        ## Simulate choice.
        y = np.apply_along_axis(categorical_logit_rng, 0, Q * beta)
        
        ## Evaluate predictions. 
        y_hat[i,j] = np.mean(Y[i,j] == y)
        a_hat[i,j] = np.mean(C[i,j] == y)
        
        ## Compute prediction error.
        delta = R[i,j] - Q[Y[i,j]]
        
        ## Assign learning rate.
        eta = np.where(delta > 0, eta_p, eta_n)
        
        ## Update Q-value.
        Q[Y[i,j]] += eta * delta
        
## Convert to DataFrames.
y_hat = DataFrame(y_hat, columns=np.arange(T)+1)
y_hat['subject'] = metrics.subject.values
y_hat['platform'] = metrics.platform.values
y_hat = y_hat.melt(id_vars=['platform','subject'], var_name='trial', value_name='choice')

a_hat = DataFrame(a_hat, columns=np.arange(T)+1)
a_hat['subject'] = metrics.subject.values
a_hat['platform'] = metrics.platform.values
a_hat = a_hat.melt(id_vars=['platform','subject'], var_name='trial', value_name='accuracy')

## Merge.
ppc = y_hat.merge(a_hat, on=['platform','subject','trial'])
ppc = ppc.sort_values(['platform','subject','trial'])

## Save.
f = os.path.join(ROOT_DIR, 'stan_results', 'rstd_ppc.tsv.gz')
ppc.to_csv(f, sep='\t', index=False, compression='gzip')