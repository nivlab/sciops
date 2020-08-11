import numpy as np
from numba import njit

@njit
def inv_logit(arr):
    """Fast inverse logistic function."""
    return 1. / (1. + np.exp(-arr))

@njit
def phi_approx(arr):
    '''Elementwise fast approximation of the cumulative unit normal.'''
    return inv_logit(0.07056 * arr ** 3 + 1.5976 * arr)

def simulate_item_response(tau, mu, xi, link='probit'):
    """Simulate ordinal responses for single item.
    
    Parameters
    ----------
    tau : array, shape (n_thresh,)
        Ordinal thresholds.
    mu : array, shape (n_sub,)
        Subject latent traits.
    xi : array, shape (n_sub,)
        Subject lapse rates.
    link : probit | inv_logit | function
        Oridinal threshold function.
        
    Returns
    -------
    Y : array, shape (n_sub, n_items)
        Ordinal responses.
    """
    
    ## Ensure arrays.
    mu = np.array(mu)
    xi = np.array(xi)
    
    ## Error-catching: 
    assert np.ndim(mu) == 1
    assert np.ndim(xi) == 1
    assert mu.size == xi.size
            
    ## Define link function.
    if link == 'probit': link = phi_approx
    elif link == 'inv_logit': link = inv_logit    
        
    ## Compute likelihood of response.
    theta = link(np.subtract.outer(tau, mu)).T
    theta = np.column_stack([np.zeros(mu.size), theta, np.ones(mu.size)])
    theta = np.diff(theta)
    
    ## Incorporate lapse.
    theta = (1 - xi[:,np.newaxis]) * theta + xi[:,np.newaxis] / theta.shape[1]
    
    ## Simulate responses.
    f = lambda p: np.random.multinomial(1,p)
    Y = np.apply_along_axis(f, 1, theta).argmax(axis=1)
    
    return Y