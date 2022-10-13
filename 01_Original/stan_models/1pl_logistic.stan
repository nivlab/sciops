/** 
* One-parameter Logistic Model w/ Random Intercepts
*
* Fits the 1-parameter item response theory model with a cumulative ordinal (logistic) link.
*  
* The 1-PL model is adapted from  Maydeu-Olivares & Coffman (2006),
* https://doi.org/10.1037/1082-989X.11.4.344
*
*/
functions {

    // Return ordinal cutpoints from a vector of response probabilities.
    vector make_cutpoints(vector pi) {
        int C = rows(pi) - 1; 
        return logit( cumulative_sum( pi[:C] ) );
    }

}
data {

    // Metadata
    int  N;                             // Number of subjects
    int  M;                             // Number of items
    int  K;                             // Number of latent factors
    
    // Data
    int  Y[N,M];                        // Self-report data

    // Design matrix
    vector[K]  X[M];                    // Design matrix

    // Prior counts
    vector[4]  C[M];                    // Number of observed responses
    
    // Mappings
    row_vector[N] pass_ix;              // Denotes subject quality (Pass = 1, Fail = 0)

}
parameters {

    // Subject-level abilities
    matrix[N,K]  Z;
    
    // Item-level difficulties
    simplex[4]  pi[M];

}
transformed parameters {

    // Ordinal cutpoints
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

    // Define contrasts matrix
    vector[3] contrasts;
    
    // Iteratively compute contrasts
    contrasts[1] = pass_ix * Z[:,1] / sum(pass_ix);
    contrasts[2] = (1-pass_ix) * Z[:,1] / sum(1-pass_ix);
    contrasts[3] = contrasts[1] - contrasts[2];
    
}