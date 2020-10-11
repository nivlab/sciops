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

# source model
source(here("stan_models", "model_library.R"))
model <- model_RW_asymmetric

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

