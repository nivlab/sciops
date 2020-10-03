#### housekeeping ####
# dependencies
require(here)

# read data and calculate sum scores
source(here("utilities", "source_data.R"))

#### metric 1: proportion correct ####
prop_correct <- as.vector(by(behav_data$accuracy, INDICES=behav_data$subject, FUN=mean))

#### metrics 2-4: win-stay rate, lose-stay rate, wsls ratio ####
prev_reward_locs    <- which(behav_data$outcome == 1 & behav_data$trial != 1) + 1
prev_nonreward_locs <- which(behav_data$outcome == 0 & behav_data$trial != 1) + 1

win_stay_rate       <- as.vector(by( data=behav_data[prev_reward_locs, "choice"] == behav_data[prev_reward_locs-1, "choice"],
                                INDICES=behav_data[prev_reward_locs, "subject"],
                                FUN=mean))
lose_stay_rate      <- as.vector(by( data=behav_data[prev_nonreward_locs, "choice"] == behav_data[prev_nonreward_locs-1, "choice"],
                                INDICES=behav_data[prev_nonreward_locs, "subject"],
                                FUN=mean))
WSLS_ratio          <- (win_stay_rate - lose_stay_rate) / (win_stay_rate + lose_stay_rate)


#### metric 5: RT difference following reward versus nonreward ####
prev_reward_rt    <- as.vector(by(behav_data[prev_reward_locs, "rt"], INDICES=behav_data[prev_reward_locs, "subject"], FUN=mean))
prev_nonreward_rt <- as.vector(by(behav_data[prev_nonreward_locs, "rt"], INDICES=behav_data[prev_nonreward_locs, "subject"], FUN=mean))
reward_rt_diff    <- prev_reward_rt - prev_nonreward_rt

#### metric 6-7: estimated learning rate and softmax inverse temperature ####
load(here("RW_symmetric_parameters.Rdata"))
RW_symm_eta <- est_pars[,2]
RW_symm_beta <- est_pars[,1]

#### metric 8 and 9: mean RT and number of long RT trials (> 1 second) ####
median_RT <- as.vector(by(behav_data$rt, INDICES=behav_data$subject, FUN=median))
n_long_RT <- as.vector(by(behav_data$rt > 1, INDICES=behav_data$subject, FUN=sum))

#### metrics 10-12: estimated learning rate, learning rate asymmetry, and  and softmax inverse temperature ####
load(here("RW_asymmetric_parameters.Rdata"))
RW_asymm_kappa <- est_pars[,3]
RW_asymm_eta <- est_pars[,2]
RW_asymm_beta <- est_pars[,1]

#### metric 13: perseveration after switch
n_perseveration <- matrix(NA, nrow=length(unique(behav_data$subject)), ncol=5)
for (i in 1:length(unique(behav_data$subject))){
  p_data <- subset(behav_data, behav_data$subject == unique(behav_data$subject)[i])
  
  switch_indices <- c(which(diff(p_data$correct) != 0) + 1, 90)

  for (j in 1:(length(switch_indices)-1)){
    choices <- p_data[switch_indices[j] : switch_indices[j+1], "choice"]
    prev_correct <- p_data[switch_indices[j]-1, "correct"]
    new_correct <- p_data[switch_indices[j], "correct"] 
    n_perseveration[i,j] <- sum(which(choices == prev_correct) < min(which(choices == new_correct)))
  }
  
}

mean_perseveration <- apply(n_perseveration, MARGIN=1, FUN=mean, na.rm=T)

#### write to csv ####

# combine metrics
all_metrics <- data.frame(survey_data$subject, survey_data$platform, prop_correct, win_stay_rate, lose_stay_rate, WSLS_ratio, reward_rt_diff, RW_symm_eta, RW_symm_beta, median_RT, n_long_RT, RW_asymm_eta, RW_asymm_beta, RW_asymm_kappa, mean_perseveration)
names(all_metrics) <- c("subject", "platform", "prop_correct", "win_stay_rate", "lose_stay_rate", "WSLS_ratio", "reward_rt_diff", "RW_symm_eta", "RW_symm_beta", "median_RT", "n_long_RT", "RW_asymm_eta", "RW_asymm_beta", "RW_asymm_kappa", "mean_perseveration")

# if file doesn't exist, write it
metric_filename <- here("..", "..", "data", "metrics.csv")
if (!file.exists(metric_filename)){
  write.csv(all_metrics, file=metric_filename, row.names=F)
} else{
  
  # otherwise, write only the columns that don't already exist
  existing_file <- as.data.frame(read.csv(metric_filename, header=T))
  existing_cols <- colnames(existing_file)
  new_metrics <- all_metrics[, !(colnames(all_metrics) %in% existing_cols)]
  new_names <- colnames(all_metrics)[!(colnames(all_metrics) %in% existing_cols)]
  all_metrics <- cbind(existing_file, new_metrics)
  colnames(all_metrics) <- c(existing_cols, new_names)
  write.csv(all_metrics, file=metric_filename, row.names=F)
  
}

