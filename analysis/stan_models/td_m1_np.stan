data {

    // Metadata
    int  N;
    int  T;
    
    // Data
    int  Y[N,T];
    int  R[N,T];
    
}
parameters {

    // Subject-level parameters (pre-transform)
    matrix[3,N]  theta_pr;

}
transformed parameters {
    
    // Subject-level parameters
    vector[N]                    beta;
    vector<lower=0, upper=1>[N]  eta_p;
    vector<lower=0, upper=1>[N]  eta_n;
    
    beta = theta_pr[1]' * 10;
    eta_p = Phi_approx( theta_pr[2] + theta_pr[3] )';
    eta_n = Phi_approx( theta_pr[2] - theta_pr[3] )';   
    
}
model {

    // Priors
    to_vector(theta_pr) ~ std_normal();

    // Main loop
    for (i in 1:N) {
    
        // Initialize Q-values
        vector[3] Q = rep_vector(0.5, 3);
    
        for (j in 1:T) {
        
            // Precompute prediction error.
            real delta = R[i,j] - Q[Y[i,j]];
            real eta = delta > 0 ? eta_p[i] : eta_n[i];
        
            // Compute choice likelihood
            Y[i,j] ~ categorical_logit( beta[i] * Q );
            
            // Update chosen Q-value.
            Q[Y[i,j]] += eta * delta;
        
        }
    
    }

}
generated quantities {

    // Log-likelihood
    vector[T]  log_lik[N];

    // Main loop
    for (i in 1:N) {
    
        // Initialize Q-values
        vector[3] Q = rep_vector(0.5, 3);
    
        for (j in 1:T) {
        
            // Precompute prediction error.
            real delta = R[i,j] - Q[Y[i,j]];
            real eta = delta > 0 ? eta_p[i] : eta_n[i];
        
            // Compute choice likelihood
            log_lik[i,j] = categorical_logit_lpmf( Y[i,j] | beta[i] * Q );
            
            // Update chosen Q-value.
            Q[Y[i,j]] += eta * delta;
        
        }
    
    }

}