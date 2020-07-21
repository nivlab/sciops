# specify model
model_RW_symmetric <- list(
  
  "model_name" = "RW_symmetric",
  "model_file" = here("stan_models", "RW_symmetric.stan"),
  "savename" = here("stan_samples", "RW_symmetric_samples.Rdata"),
  "par_savename" = here("RW_symmetric_parameters.Rdata"),
  "parameters" = c( "beta_mu",
                    "eta_mu",
                    "sigma",
                    "beta",
                    "eta",
                    "choice_log_likelihood",
                    "choice_pred"),
  "indiv_parameters" = c("beta",
                         "eta")
) 

model_RW_asymmetric <- list(
  
  "model_name" = "RW_asymmetric",
  "model_file" = here("stan_models", "RW_asymmetric.stan"),
  "savename" = here("stan_samples", "RW_asymmetric_samples.Rdata"),
  "par_savename" = here("RW_asymmetric_parameters.Rdata"),
  "parameters" = c( "beta_mu",
                    "eta_mu",
                    "kappa_mu",
                    "sigma",
                    "beta",
                    "eta",
                    "kappa",
                    "choice_log_likelihood",
                    "choice_pred"),
  "indiv_parameters" = c("beta",
                         "eta",
                         "kappa")
) 