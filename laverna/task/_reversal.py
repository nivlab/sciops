"""Multi-arm reversal learning task."""

import numpy as np
from numba import njit

@njit
def softmax(arr):
    """Scale-robust softmax function"""
    arr = np.exp(arr - np.max(arr))
    return arr / arr.sum()


def simulate_reversal_task(blocks, n_arms=3, p_target=0.8, p_other=0.2, size=1):
    """Simulate games of reversal learning task.
    
    Parameters
    ----------
    blocks : array, shape (n_blocks,)
        Array of ints, each denoting the length of a block.
    n_arms : int
        Number of bandit arms.
    p_target : float in range [0-1]
        Probability of reward for target arm.
    p_other: float in range [0-1]
        Probability of reward for remaining arms.
    size: int
        Number of games to simulate
        
    Returns
    -------
    rewards : array, shape (n_games, n_trials, n_arms)
        Binary rewards.
    pi : array, shape (n_games, n_blocks)
        Optimal choice.
    """
    
    ## Initialize targets.
    P = np.random.multinomial(1, np.ones(n_arms) / n_arms, size)
    P = np.where(P, p_target, p_other)
    
    ## Main loop.
    R = []; pi = [] 
    for n_trials in blocks:
        
        ## Store optimal choice.
        pi.append(P.argmax(axis=1))
        
        ## Simulate block of outcomes. Store.
        r = np.random.binomial(1, P, size=(n_trials,size,n_arms))
        R.append(r)
    
        ## Iteratively shift rows.
        for i, j in enumerate(np.random.choice([1,-1], size, replace=True)):
            P[i] = np.roll(P[i], j)
                
    ## Concatenate outcomes.
    R = np.row_stack(R).swapaxes(0,1)
    pi = np.stack(pi, axis=1)
                
    return R, pi


class ReversalTask(object):
    """Train agents on reversal learning task. 
    
    Parameters
    ----------
    beta : array, shape (n_agents,)
        Inverse temperature.
    eta : array, shape (n_agents,)
        Learning rate (between 0 & 1).
    xi : array, shape (n_agents,)
       Lapse rate (between 0 & 1).    
    """
    
    def __init__(self, beta, eta, xi):
        
        ## Define parameters.
        self.beta = np.array(beta)
        self.eta  = np.array(eta)
        self.xi   = np.array(xi)
        
        ## Error-catching.
        if np.any(np.diff([self.beta.size, self.eta.size, self.xi.size])):
            return ValueError('Parameters must be of same length.')
        
        ## Define metadata.
        self.n_agents = self.beta.size
        self._ix = np.arange(self.n_agents).astype(int)
        
        ## Initialize Q-values.
        self.Q = None

    def __repr__(self):
        return f'<reversal learning (n = {self.n_agents})>'
        
    def train(self, R, q0=0., reset=False):
        """Train Q-values.
        
        Parameters
        ----------
        R : array, shape (n_agents, n_trials, n_arms)
            Reward for each agent, trial, and arm.
        q0 : float
            Initial Q-value.
        reset : True | False
            If True, re-initialize Q-values at start of training.
            
        Returns
        -------
        Y : array, shape (n_agents, n_trials)
            Chosen action.
        """
        
        ## Define metadata.
        n_agents, n_trials, n_arms = R.shape
        if not self.n_agents == n_agents:
            raise ValueError('Number of games does not much number of agents.')
        
        ## Initialize Q-values.
        if self.Q is None or reset:
            self.Q = float(q0) * np.ones((n_agents, n_arms), dtype=float)
            
        ## Preallocate space.
        Y = np.ones((n_agents, n_trials), dtype=int)
        
        ## Main loop.
        for i in range(n_trials):
            
            ## Compute choice likelihood.
            theta = np.apply_along_axis(softmax, 1, self.Q * self.beta[:,np.newaxis])
            theta = (1 - self.xi[:,np.newaxis]) * theta + (self.xi[:,np.newaxis] / n_arms)
            
            ## Simulate choice.
            f = lambda p: np.random.multinomial(1,p)
            Y[:,i] = np.apply_along_axis(f, 1, theta).argmax(axis=1)
            
            ## Observe outcomes.
            r = R[self._ix, i, Y[:,i]]
            
            ## Update action-values.
            self.Q[self._ix, Y[:,i]] += self.eta * ( r - self.Q[self._ix, Y[:,i]] )
            
        return Y