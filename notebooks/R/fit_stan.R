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

# specify parallel options for stan
rstan_options(auto_write = TRUE)
options(mc.cores = parallel::detectCores(), buildtools.check = function(action) TRUE)

# sample from model
tic()
samples <- stan(file   = model$model_file,         # file containing stan code
                data   = stan_data,                # list containing stan data
                pars   = model$parameters,         # parameters to monitor
                iter   = 250,                      # total samples to draw
                warmup = 150,                      # unmonitored samples
                chains = 2,                        # number of parallel chains 
                thin   = 1,                         # thinning factor
                save_warmup = TRUE
)
toc()

# print and/or save samples
print(samples)
save(list=c("samples"), file=model$savename)

