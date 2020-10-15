import h5py, os, pystan
import numpy as np
from os.path import dirname
from pandas import DataFrame, read_csv
from scipy.stats import norm
from stantools.io import load_model
from stantools.model import waic
from stantools.stats import phi_approx
ROOT_DIR = dirname(dirname(os.path.realpath(__file__)))

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### Define parameters.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

## I/O parameters.
stan_model = 'td_m1_np'

## Sampling parameters.
samples = 2000
warmup = 1500
chains = 4
thin = 1
n_jobs = 4

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### Load and prepare data.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

## Load data.
data = read_csv(os.path.join(ROOT_DIR, 'data', 'data.csv'))

## Restrict participants.
reject = read_csv(os.path.join(ROOT_DIR, 'data', 'reject.csv'))
data = data[data.subject.isin(reject.subject)].reset_index(drop=True)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### Assemble data for Stan.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

## Define metadata.
N = data.subject.nunique()
T = data.trial.nunique()

## Define data.
Y = data.pivot_table('choice','subject','trial').values.astype(int) + 1
R = data.pivot_table('outcome','subject','trial').values.astype(int)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### Fit Stan Model.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

## Assemble data.
dd = dict(N=N, T=T, Y=Y, R=R)

## Load StanModel
StanModel = load_model(os.path.join(ROOT_DIR,'stan_models',stan_model))

## Fit model.
StanFit = StanModel.sampling(data=dd, iter=samples, warmup=warmup, chains=chains, thin=thin, n_jobs=n_jobs, seed=47404)
        
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### Model comparison.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

## Extract parameters.
StanDict = StanFit.extract()
log_lik = StanDict['log_lik']

## Compute per-subject likelihood.
Y_pred = np.apply_over_axes(np.mean, np.exp(log_lik), [0,2]).squeeze()

## Compute WAIC.
log_lik = log_lik.reshape(log_lik.shape[0], -1)
WAIC = waic(log_lik).reshape(Y.shape).sum(axis=1)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### Save data.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
print('Saving data.')

## Save summary file.
summary = StanFit.summary()
summary = DataFrame(summary['summary'], columns=summary['summary_colnames'],
                    index=summary['summary_rownames'])
summary = summary.loc[[s for s in summary.index if not s.startswith('log_lik')]]
summary.to_csv(os.path.join(ROOT_DIR,'stan_results',f'{stan_model}.csv'))

## Save parameters.    
with h5py.File(os.path.join(ROOT_DIR, 'stan_results', f'{stan_model}_mcmc.hdf5'), 'w') as f:
        
    ## Iteratively add Stan samples.
    for k, v in StanDict.items():
        if k == 'lp__': continue
        f.create_dataset(k, data=np.median(v, axis=0))
    
    ## Add posterior predictive likelihood. 
    f.create_dataset(f'Y_pred', data=Y_pred)
    
    ## Add model comparison.
    f.create_dataset(f'WAIC', data=WAIC)