/** 
* Risk sensitive temporal difference learning
*
* The RSTD model is a temporal difference learning model (Sutton and Barto, 2018)
* where the value of choice options are learned through the accumulation
* of reward prediction errors. The RSTD allows positive and negative prediction 
* errors to have asymmetric effects on learning.
*
* The RSTD model is adapted from Niv et al. (2012),
* https://doi.org/10.1523/JNEUROSCI.5498-10.2012
*
*/
data {

    // Metadata
    int  N;                         // Number of subjects
    int  T;                         // Number of trials
    
    // Data
    int  Y[N,T];                    // Choice data
    int  R[N,T];                    // Reward data 
    
}
parameters {

    // Subject-level parameters (pre-transform)
    matrix[3,N]  theta_pr;

}
transformed parameters {
    
    // Subject-level parameters
    vector[N]                    beta;     // Inverse temperature
    vector<lower=0, upper=1>[N]  eta_p;    // Learning rate (positive prediction errors)
    vector<lower=0, upper=1>[N]  eta_n;    // Learning rate (negative prediction errors)
    
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
            
            // Assign learning rate.
            real eta = delta > 0 ? eta_p[i] : eta_n[i];
        
            // Compute choice likelihood
            Y[i,j] ~ categorical_logit( beta[i] * Q );
            
            // Update chosen Q-value.
            Q[Y[i,j]] += eta * delta;
        
        }
    
    }

}