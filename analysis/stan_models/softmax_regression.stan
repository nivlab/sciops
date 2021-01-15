/** 
* Softmax Regression
*
* The softmax regression model estimates the impact of rewards, nonrewards, 
* and previous choices from successively distant choices on future choices. 
* For rewards and nonrewards, the model estimates the decision weight, which 
* represents the bias to choose a particular option according to the outcome 
* experienced from selection of that option in the recent past. Separately,
* the model accounts for the inherent tendency to repeat choices regardless 
* of outcomes (i.e., perseveration). 
*
* The softmax regession model is adapted from Seymour et al. (2012),
* https://doi.org/10.1523/JNEUROSCI.0053-12.2012.
*
*/
data {

    // Metadata
    int  N;                         // Number of subjects
    int  K;                         // Number of arms
    int  L;                         // Number of lags
    int  T;                         // Number of trials
    
    // Data
    int  Y[N,T];                    // Choice data
    
    // Design matrices
    matrix[T,L*3]  X[N,K];          // History of rewards, nonrewards, and choices
    
    // Mappings
    vector[N] pass_ix;              // Denotes subject quality (Pass = 1, Fail = 0)

}
parameters {

    // Regression weights
    matrix[L*3,N]  W;

}
model {
    
    // Priors
    to_vector(W) ~ normal(0, 5);
    
    // Main loop
    for (i in 1:N) {
                
        // Compute sum of weights per arm
        matrix[T,K]  beta;
        for (k in 1:K) { beta[:,k] = X[i,k] * W[:,i]; }
        
        // Iteratively compute choice likelihood
        for (j in 1:T) { Y[i,j] ~ categorical_logit( beta[j]' ); }
    
    }

}
generated quantities {

    // Define contrasts matrix
    matrix[15,3] contrasts;
    
    // Iteratively compute contrasts
    for (i in 1:15) {
        contrasts[i,1] = W[i] * pass_ix / sum(pass_ix);
        contrasts[i,2] = W[i] * (1-pass_ix) / sum(1-pass_ix);
        contrasts[i,3] = contrasts[i,1] - contrasts[i,2];
    }
    
}