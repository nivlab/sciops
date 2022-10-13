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
stan_model = 'softmax_regression'

## Model parameters.
L = 5

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

## Define reject index.
pass_ix = np.where(metrics.infreq > 0, 0, 1)

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
dd = dict(N=N, K=K, L=L, T=T, X=X, Y=Y, pass_ix=pass_ix)

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
