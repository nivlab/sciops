data {

    // Metadata
    int  N;                  // Number of subjects
    int  K;                  // Number of arms
    int  T;                  // Number of trials
    
    // Data
    matrix[T,15]  X[N,K];    // Design matrices
    int           Y[N,T];    // Choice data
    
    // Subject-mapping
    row_vector<lower=0,upper=1>[N] reject_ix; 

}
parameters {

    // Subject-level parameters
    matrix[15,N]  W;

}
model {
    
    // Priors
    to_vector(W) ~ normal(0, 5);
    
    // Main loop
    for (i in 1:N) {
        
        // Preallocate space
        matrix[T,3]  Q;
        
        // Iteratively compute Q-values
        for (j in 1:K) { Q[:,j] = X[i,j] * W[:,i]; }
        
        // Iteratively compute choice likelihood
        for (j in 1:T) { Y[i,j] ~ categorical_logit( Q[j]' ); }
    
    }

}
generated quantities {

    matrix[15,3] contrasts;
    
    for (i in 1:15) {
        contrasts[i,1] = sum( (1-reject_ix) .* W[i] ) / sum(1-reject_ix);
        contrasts[i,2] = sum( reject_ix .* W[i] ) / sum(reject_ix);
        contrasts[i,3] = contrasts[i,1] - contrasts[i,2];
    }
    
}