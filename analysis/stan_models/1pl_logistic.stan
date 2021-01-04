functions {

    vector make_cutpoints(vector pi) {
        int C = rows(pi) - 1; 
        return logit( cumulative_sum( pi[:C] ) );
    }

}
data {

    // Metadata
    int  N;                             // Number of subjects
    int  M;                             // Number of items
    int  K;                             // Number of regressors
    
    // Data
    int  Y[N,M];                        // Self-report data

    // Design matrix
    vector[K]  X[M];                    // Design matrix

    // Prior counts
    vector[4]  C[M];                    // Number of observed responses
    
    // Mappings
    vector[N]  fail_ix;                 // Index of C/IE participants

}
parameters {

    // Subject-level parameters
    matrix[N,K]  Z;
    
    // Item-level difficulties
    simplex[4]  pi[M];

}
transformed parameters {

    ordered[3]  kappa[M];
    for (m in 1:M)  { kappa[m] = make_cutpoints( pi[m] ); }

}
model {

    // Subject-level priors
    to_vector(Z) ~ normal(0,1);    
    
    // Item-level priors (difficulties)
    for (m in 1:M)  { pi[m] ~ dirichlet(C[m]); }

    // Likelihood
    for (m in 1:M) {
        target += ordered_logistic_glm_lpmf( Y[:,m] | Z, X[m], kappa[m] );
    }

}
generated quantities {

    vector[3] contrasts;
    contrasts[1] = sum( (1-fail_ix) .* Z[:,1] ) / sum(1-fail_ix);
    contrasts[2] = sum( fail_ix .* Z[:,1] ) / sum(fail_ix);
    contrasts[3] = contrasts[1] - contrasts[2];
    
}