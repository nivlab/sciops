// Risk-sensitive learning task model
// Symmetric learning rates for positive and negative RPEs
// with partial pooling
//
// Parameters (2): 
//   - beta: inverse temperature
//   - eta:  learning rate
data {
  
  // Metadata
  int  N;               // Number of subjects
  int  T;               // Number of trials per participant
  
  // Data
  int Y[T];             // Choices
  int R[T];             // Rewards
  
  // Mappings
  int subj_ix[T];                 // Trial-to-participant mapping
  int new_subj_ix[T];             // 1/0 indicator: is this participant on this trial different from the participant on the previous trial?

}
transformed data {
  
  // Upper limit of inverse tmperature
  real  ul = 20;
  
  // Number of bandits
  int   n_bandits = 3;
  
  // Initial bandit value
  real  init_bandit_q = 0.5;
  
}
parameters {
  
  // Group-level parameters
  real                beta_mu_pr;
  real                eta_mu_pr;
  vector<lower=0>[2]  sigma;
  
  // subject-level parameters
  vector[N] beta_pr;              // inverse temperature
  vector[N] eta_pr;               // learning rate
  
}
transformed parameters {
  
  vector<lower=0, upper=ul>[N] beta;  // inverse temperature
  vector<lower=0, upper=1>[N]  eta;   // learning rate
  
  // create participant parameter vectors  
  beta = Phi_approx(beta_mu_pr + sigma[1] * beta_pr) * ul;
  eta  = Phi_approx( eta_mu_pr + sigma[2] * eta_pr);
  
}
model {
  
  // Generated quantities
  vector[n_bandits]   Q = rep_vector(init_bandit_q, n_bandits);   // Set stimulus values
  vector[n_bandits]   theta[T];                                   // Parameters of softmax

  // group-level priors
  beta_mu_pr ~ normal(0, 1);
  eta_mu_pr  ~ normal(0, 1);
  sigma      ~ normal(0, 2);
  
  // subject-level priors
  beta_pr    ~ normal(0, 1);
  eta_pr     ~ normal(0, 1);
  
  // loop over trials  
  for (t in 1:T) {
    
    if (new_subj_ix[t] == 1){
      Q = rep_vector(init_bandit_q, n_bandits);   // Set stimulus values  
    }
    
    // assign probability to choice
    theta[t] = beta[subj_ix[t]] * Q;
    Y[t]     ~ categorical_logit(theta[t]);
    
    // Update action value of chosen action
    Q[Y[t]] += eta[subj_ix[t]] * (R[t] - Q[Y[t]]);

  }
  
}
generated quantities {
  
  // Group-level parameters
  real beta_mu = Phi_approx(beta_mu_pr) * ul;
  real eta_mu  = Phi_approx(eta_mu_pr);
  
  // generated quantities
  vector[T]         choice_log_likelihood;                        // log likelihood of choice per model
  vector[T]         choice_pred;                                  // synthetic choice vector of same length as actual choices
  vector[n_bandits]   Q = rep_vector(init_bandit_q, n_bandits);   // Set stimulus values
  vector[n_bandits]   theta[T];                                   // Parameters of softmax
  
  // loop over trials  
  for (t in 1:T) {
    
    if (new_subj_ix[t] == 1){
      Q = rep_vector(init_bandit_q, n_bandits);   // Set stimulus values  
    }
    
    // assign probability to choice
    theta[t] = beta[subj_ix[t]] * Q;

    // Update action value of chosen action
    Q[Y[t]] += eta[subj_ix[t]] * (R[t] - Q[Y[t]]);
    
    // calculate choice likelihood
    choice_log_likelihood[t] = categorical_logit_lpmf( Y[t] | theta[t] );
    
    // simulate a choice
    choice_pred[t] = categorical_logit_rng( theta[t] );

  }
  
}
