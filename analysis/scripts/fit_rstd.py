import os
import numpy as np
from os.path import dirname
from pandas import DataFrame, read_csv
from cmdstanpy import CmdStanModel, set_cmdstan_path
set_cmdstan_path('/path/to/cmdstan')
ROOT_DIR = dirname(dirname(os.path.realpath(__file__)))

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### Define parameters.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

## I/O parameters.
stan_model = 'rstd'

## Sampling parameters.
iter_warmup   = 1500
iter_sampling = 500
chains = 4
thin = 1
parallel_chains = 4

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### Load and prepare data.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

## Load data.
data = read_csv(os.path.join(ROOT_DIR, 'data', 'data.csv'))

## Restrict participants.
metrics = read_csv(os.path.join(ROOT_DIR, 'data', 'metrics.csv'))
data = data[data.subject.isin(metrics.subject)].reset_index(drop=True)

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
summary.to_csv(os.path.join(ROOT_DIR, 'stan_results', f'{stan_model}_{D}d_summary.tsv'), sep='\t')

## Extract and save samples.
samples = StanFit.draws_pd()
samples.to_csv(os.path.join(ROOT_DIR, 'stan_results', f'{stan_model}_{D}d.tsv'), sep='\t', index=False)
