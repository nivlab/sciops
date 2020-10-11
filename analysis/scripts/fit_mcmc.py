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
samples = 4000
warmup = 2000
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
### Posterior predictive check.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
np.random.seed(47404)

## Define useful functions.
def softmax(arr):
    """Scale-robust softmax choice rule."""
    arr = np.exp(arr - np.max(arr))
    return arr / arr.sum()

def categorical_rng(p):
    return np.argmax(np.random.multinomial(1,p))

## Extract parameters.
StanDict = StanFit.extract()

## Unpack parameters.
beta = StanDict['beta']
eta_p = StanDict['eta_p']
eta_n = StanDict['eta_n']

## Preallocate space.
S = beta.shape[0]
Y_pred = np.zeros((S, *Y.shape)).astype(float)
Y_hat = np.zeros((S, *Y.shape)).astype(float)

## Main loop.
for i in range(N):
    
    ## Initialize Q-values.
    Q = 0.33 * np.ones((S, 3))
    
    for j in range(T):
        
        ## Compute choice probabilities.
        theta = np.apply_along_axis(softmax, 1, beta[:,i,np.newaxis] * Q)
        
        ## Compute choice likelihood.
        Y_pred[:,i,j] = theta[:,Y[i,j]-1]
        
        ## Simulate choice.
        Y_hat[:,i,j] = np.apply_along_axis(categorical_rng, 1, theta)
        
        ## Compute reward prediction error.
        delta = R[i,j] - Q[:,Y[i,j]-1]
        
        ## Update Q-values.
        Q[:,Y[i,j]-1] += np.where(delta > 0, eta_p[:,i], eta_n[:,i]) * delta
        
## Compress simulated choice.
Y_hat = np.apply_along_axis(np.bincount, 0, Y_hat.astype(int), minlength=3)
Y_hat = np.moveaxis(Y_hat, 0, 2)
        
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### Model comparison.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

## Compute WAIC.
log_lik = Y_pred.reshape(S, -1)
log_lik = np.log(log_lik)
WAIC = waic(log_lik).reshape(Y.shape).sum(axis=1)

## Compress choice likelihood.
Y_pred = np.median(Y_pred, axis=0)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
### Save data.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
print('Saving data.')

## Save summary file.
summary = StanFit.summary()
summary = DataFrame(summary['summary'], columns=summary['summary_colnames'],
                    index=summary['summary_rownames'])
summary.to_csv(os.path.join(ROOT_DIR,'stan_results',f'{stan_model}.csv'))

## Save parameters.    
with h5py.File(os.path.join(ROOT_DIR, 'stan_results', f'{stan_model}_mcmc.hdf5'), 'w') as f:
        
    ## Add pre-transform parameters.
    f.create_dataset('theta_pr', data=np.median(theta_pr, axis=0))
        
    ## Add reconstructed parameters.
    f.create_dataset('beta', data=np.median(beta, axis=0))
    f.create_dataset('eta_p', data=np.median(eta_p, axis=0))
    f.create_dataset('eta_n', data=np.median(eta_n, axis=0))
        
    ## Add posterior predictive check.
    f.create_dataset(f'Y_hat', data=Y_hat)
    
    ## Add posterior predictive likelihood. 
    f.create_dataset(f'Y_pred', data=Y_pred)
    
    ## Add model comparison.
    f.create_dataset(f'WAIC', data=WAIC)