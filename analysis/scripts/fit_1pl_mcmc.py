import h5py, os, pystan
import numpy as np
from os.path import dirname
from pandas import DataFrame, read_csv
from stantools.io import load_model
ROOT_DIR = dirname(dirname(os.path.realpath(__file__)))

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### Define parameters.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

## I/O parameters.
stan_model = '1pl_logistic'

## Sampling parameters.
samples = 2000
warmup = 1500
chains = 4
thin = 1
n_jobs = 4

## Define subscales.
subscales = [
    ['7u7d-q01','7u7d-q03','7u7d-q04','7u7d-q06','7u7d-q07','7u7d-q08','7u7d-q12'],
    ['7u7d-q02','7u7d-q05','7u7d-q09','7u7d-q10','7u7d-q11','7u7d-q13','7u7d-q14'],
    ['gad7-q01','gad7-q02','gad7-q03','gad7-q04','gad7-q05','gad7-q06','gad7-q07'],
    ['bisbas-q01','bisbas-q02','bisbas-q03','bisbas-q04'],
    ['bisbas-q05','bisbas-q06','bisbas-q07','bisbas-q08'],
    ['bisbas-q09','bisbas-q10','bisbas-q11','bisbas-q12'],
    ['shaps-q01','shaps-q02','shaps-q03','shaps-q04','shaps-q05',
     'shaps-q06','shaps-q07','shaps-q08','shaps-q09','shaps-q10',
     'shaps-q11','shaps-q12','shaps-q13','shaps-q14'],
]

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### Load and prepare data.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

## Load survey data.
surveys = read_csv(os.path.join(ROOT_DIR, 'data','surveys.csv'))

## Restrict participants.
reject = read_csv(os.path.join(ROOT_DIR, 'data', 'reject.csv'))
surveys = surveys[surveys.subject.isin(reject.subject)].reset_index(drop=True)

## Restrict to desired items.
surveys = surveys[np.concatenate(subscales)]

## Undo BIS/BAS reverse scoring.
cols = surveys.filter(regex='bisbas').columns
surveys[cols] = 3 - (surveys[cols] - 1)

## Undo SHAPS reverse scoring.
cols = surveys.filter(regex='shaps').columns
surveys[cols] = 3 - surveys[cols]

## Make items 1-indexed.
surveys += 1

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### Assemble data for Stan.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

## Define metadata.
N, T = surveys.shape
K = len(subscales)

## Define data.
Y = surveys.values.astype(int)

## Define mappings.
reject_ix = np.where(reject.infreq > 0, 1, 0)
scale_ix = np.concatenate([np.repeat(i, len(v)) for i, v in enumerate(subscales)]) + 1

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### Fit Stan Model.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

## Assemble data.
dd = dict(N=N, K=K, T=T, Y=Y, reject_ix=reject_ix, scale_ix=scale_ix)

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