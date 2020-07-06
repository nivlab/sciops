#### housekeeping ####
# dependencies
require(here)

# read data and calculate sum scores
source(here("utilities", "sum_scores.R"))

#### metric 1: proportion correct ####
prop_correct <- as.vector(by(behav_data$accuracy, INDICES=behav_data$subject, FUN=mean))

#### metrics 2-4: win-stay rate, lose-stay rate, wsls ratio ####
behav_data$win_stay <- NA
behav_data$lose_stay <- NA
for (i in 1:dim(behav_data)[1]){
  
  if (behav_data$trial[i] == 1){
    next
  } else if (behav_data$outcome[i-1] == 1){
    
    if (behav_data$choice[i] == behav_data$choice[i-1]){
      behav_data$win_stay[i] <- 1
    } else {
      behav_data$win_stay[i] <- 0
    }
    
  } else if (behav_data$outcome[i-1] == 0){
    
    if (behav_data$choice[i] == behav_data$choice[i-1]){
      behav_data$lose_stay[i] <- 1
    } else {
      behav_data$lose_stay[i] <- 0
    }
    
  }
  
}
win_stay_rate <- as.vector(by(behav_data$win_stay, INDICES=behav_data$subject, FUN=mean, na.rm=T))
lose_stay_rate <- as.vector(by(behav_data$lose_stay, INDICES=behav_data$subject, FUN=mean, na.rm=T))
WSLS_ratio <- (win_stay_rate - lose_stay_rate) / (win_stay_rate + lose_stay_rate)


#### metric 5: RT difference following reward versus nonreward ####
prev_reward_locs <- which(behav_data$outcome == 1 & behav_data$trial != 1) + 1
prev_nonreward_locs <- which(behav_data$outcome == 0 & behav_data$trial != 1) + 1

prev_reward_rt <- as.vector(by(behav_data[prev_reward_locs, "rt"], INDICES=behav_data[prev_reward_locs, "subject"], FUN=mean))
prev_nonreward_rt <- as.vector(by(behav_data[prev_nonreward_locs, "rt"], INDICES=behav_data[prev_nonreward_locs, "subject"], FUN=mean))

reward_rt_diff <- prev_reward_rt - prev_nonreward_rt
