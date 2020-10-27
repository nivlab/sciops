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
stan_model = 'softmax_regression'

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

## Define reject index.
reject_ix = np.where(reject.infreq > 0, 1, 0)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### Assemble data for Stan.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

## Define metadata.
N = data.subject.nunique()
K = data.choice.nunique()
T = data.trial.nunique()

## Define convenience function.
f = lambda x: np.roll(x, 1)

## Define previous choice.
data['prev_choice'] = data.groupby(['platform','subject']).choice.transform(f)

## Main loop.
X = []
for k in range(3):

    ## Iteratively construct lags.
    for i in range(5):

        ## First lag.
        if not i:

            ## Initialize previous reward kernel.
            data[f'x{i+1}'] = data.groupby(['platform','subject']).outcome.transform(f)
            data[f'x{i+1}'] *= np.where(data.prev_choice==k, 1, 0)  
            
            ## Initialize previous choice kernel.
            data[f'x{i+6}'] = 1 - data.groupby(['platform','subject']).outcome.transform(f)
            data[f'x{i+6}'] *= np.where(data.prev_choice==k, 1, 0)  

            ## Initialize previous choice kernel.
            data[f'x{i+11}'] = data.groupby(['platform','subject']).choice.transform(f)
            data[f'x{i+11}'] = np.where(data.prev_choice==k, 1, -1)  

        else:

            ## Shift previous reward kernel.
            data[f'x{i+1}'] = data.groupby(['platform','subject'])[f'x{i}'].transform(f)
            
            ## Shift previous non-reward kernel.
            data[f'x{i+6}'] = data.groupby(['platform','subject'])[f'x{i+5}'].transform(f)

            ## Shift previous choice kernel
            data[f'x{i+11}'] = data.groupby(['platform','subject'])[f'x{i+10}'].transform(f)

        ## Mask previous lags.
        data.loc[:i,(f'x{i+1}',f'x{i+6}',f'x{i+11}')] = 0
        
    ## Reshape data. Append.
    cols = [f'x{i+1}' for i in range(15)]
    x = data.pivot_table(cols, ['platform','subject'], 'trial')[cols].values.reshape(N,15,T).swapaxes(1,2)
    X.append(x)

## Concatenate data.
X = np.stack(X, axis=1)

## Prepare choice data.
Y = data.pivot_table('choice', ['platform','subject'], 'trial').values.astype(int) + 1

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### Fit Stan Model.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

## Assemble data.
dd = dict(N=N, K=K, T=T, X=X, Y=Y, reject_ix=reject_ix)

## Load StanModel
StanModel = load_model(os.path.join(ROOT_DIR,'stan_models',stan_model))

## Fit model.
StanFit = StanModel.sampling(data=dd, iter=samples, warmup=warmup, chains=chains, thin=thin, n_jobs=n_jobs, seed=47404)

## Extract parameters.
StanDict = StanFit.extract()

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
        elif k == 'contrasts': f.create_dataset(k, data=v)
        else: f.create_dataset(k, data=np.median(v, axis=0))
