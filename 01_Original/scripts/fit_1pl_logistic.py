import os
import numpy as np
from os.path import dirname
from pandas import read_csv, get_dummies
from cmdstanpy import CmdStanModel, set_cmdstan_path
set_cmdstan_path('/path/to/cmdstan')
ROOT_DIR = dirname(dirname(os.path.realpath(__file__)))

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### Define parameters.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

## I/O parameters.
stan_model = '1pl_logistic'

## Sampling parameters.
iter_warmup   = 1500
iter_sampling = 500
chains = 4
thin = 1
parallel_chains = 4

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### Load and prepare data.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

## Load survey data.
items = read_csv(os.path.join(ROOT_DIR, 'data', 'items.csv'))

## Restrict participants.
metrics = read_csv(os.path.join(ROOT_DIR, 'data', 'metrics.csv'))
items = items[items.subject.isin(metrics.subject)].reset_index(drop=True)

## Drop PSWQ.
cols = items.filter(regex='pswq').columns
items = items.drop(columns=cols)

## Align BIS/BAS scores as presented.
cols = items.filter(regex='b[i,a]s').columns
items[cols] = 3 - (items[cols] - 1)

## Align SHAPS scores as presented.
cols = items.filter(regex='shaps').columns
items[cols] = 3 - items[cols]

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### Assemble data for Stan.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

## Define data.
Y = items.filter(regex='_').values + 1

## Define design matrix.
X = ['_'.join(k.split('_')[:-1]) for k in items.filter(regex='_').columns.tolist()]
X = get_dummies(X)[['7u','7d','gad7','bis','bas','shaps']].values
X = np.column_stack([np.ones(X.shape[0]), X])

## Define counts.
C = np.apply_along_axis(np.bincount, 0, Y-1, minlength=4).T + 1

## Define fail index.
pass_ix = np.where(metrics.infreq > 0, 0, 1)

## Define metadata.
N, M = Y.shape
M, K = X.shape

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### Fit Stan Model.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

## Assemble data.
dd = dict(N=N, M=M, K=K, Y=Y, X=X, C=C, fail_ix=fail_ix)

## Load StanModel
StanModel = CmdStanModel(stan_file=os.path.join(ROOT_DIR,'stan_models',f'{stan_model}.stan'))

## Fit Stan model.
StanFit = StanModel.sample(data=dd, chains=chains, iter_warmup=iter_warmup, iter_sampling=iter_sampling, 
                           thin=thin, parallel_chains=parallel_chains, seed=0, show_progress=True)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### Save samples.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
print('Saving data.')

## Extract and save Stan summary.
summary = StanFit.summary()
summary.to_csv(os.path.join(ROOT_DIR, 'stan_results', f'{stan_model}_summary.tsv'), sep='\t')

## Extract and save samples.
samples = StanFit.draws_pd()
samples.to_csv(os.path.join(ROOT_DIR, 'stan_results', f'{stan_model}.tsv.gz'), sep='\t', index=False, compression='gzip')