data {

    // Metadata
    int  N;
    int  T;
    
    // Data
    int  Y[N,T];
    int  R[N,T];
    
}
transformed data {

    // Indices of unchosen options
    int ix[3, 2] = { {2, 3}, {1, 3}, {1,2} };

}
parameters {

    // Subject-level parameters (pre-transform)
    matrix[4,N]  theta_pr;

}
transformed parameters {
    
    // Subject-level parameters
    vector[N]  beta  = theta_pr[1]' * 10;
    vector[N]  eta_p = Phi_approx( theta_pr[2] + theta_pr[3] )';
    vector[N]  eta_n = Phi_approx( theta_pr[2] - theta_pr[3] )';
    vector[N]  eta_d = Phi_approx( theta_pr[4] )';
    
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
            
            // Update unchosen Q-values.
        
        }
    
    }

}