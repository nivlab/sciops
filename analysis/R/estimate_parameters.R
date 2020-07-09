# dependencies
require(here)
require(rstan)
require(tictoc)

# read in behavioural data and merge
prolific    <- read.csv(here("..", "..", "data", "prolific", "data", "data.csv"), header=T)
turk        <- read.csv(here("..", "..", "data", "mturk", "data", "data.csv"), header=T)
behav_data  <- as.data.frame(rbind(prolific,turk))

# optionally subset data
behav_data <- subset(behav_data, behav_data$subject %in% unique(behav_data$subject)[1:20])

# format data for stan
stan_data <- list(
  "N"           = length(unique(behav_data$subject)),
  "T"           = dim(behav_data)[1],
  "Y"           = behav_data$choice + 1,
  "R"           = behav_data$outcome,
  "subj_ix"     = as.numeric(behav_data$subject),
  "new_subj_ix" = 1 * (behav_data$trial == 1)
)

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
model <- model_RW_symmetric

# load in samples
load(model$savename)

# loop over estimated parameters per participant
est_pars <- NULL
par_name <- NULL
for (i in 1:length(model$indiv_parameters)){
  par <- extract(samples, pars = model$indiv_parameters[[i]])[[1]]
  est_pars <- cbind(est_pars, apply(par, MARGIN=2, FUN=median))
  par_name <- c(par_name, model$indiv_parameters[[i]])
}

colnames(est_pars) <- par_name

save(est_pars, file=model$par_savename)

