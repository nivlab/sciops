# dependencies
require(here)

# read in behavioural data and merge
prolific    <- read.csv(here("..", "..", "data", "prolific", "data", "data.csv"), header=T)
turk        <- read.csv(here("..", "..", "data", "mturk", "data", "data.csv"), header=T)
behav_data  <- as.data.frame(rbind(prolific,turk))

# read in survey data and merge
prolific    <- read.csv(here("..", "..", "data", "prolific", "data", "surveys.csv"), header=T)
turk        <- read.csv(here("..", "..", "data", "mturk", "data", "surveys.csv"), header=T)
survey_data <- as.data.frame(rbind(prolific,turk))

# calculate sum scores and infrequency check for 7up 7down
survey_data$seven_up          <- rowSums(survey_data[, c("X7u7d.q01", "X7u7d.q03", "X7u7d.q04", "X7u7d.q06", "X7u7d.q07", "X7u7d.q08", "X7u7d.q13")])
survey_data$seven_down        <- rowSums(survey_data[, c("X7u7d.q02", "X7u7d.q05", "X7u7d.q09", "X7u7d.q10", "X7u7d.q11", "X7u7d.q12", "X7u7d.q14")])
survey_data$susd_infreq_pass  <- survey_data[, "X7u7d.q15"] == 0

# calculate sum scores and infrequency check for BISBAS
survey_data$bis                <- rowSums(survey_data[, c("bisbas.q01", "bisbas.q02", "bisbas.q03", "bisbas.q04")])
survey_data$bas_rwd            <- rowSums(survey_data[, c("bisbas.q05", "bisbas.q06", "bisbas.q07", "bisbas.q08")])
survey_data$bas_drive          <- rowSums(survey_data[, c("bisbas.q09", "bisbas.q10", "bisbas.q11", "bisbas.q12")])
survey_data$bisbas_infreq_pass <- survey_data[, "bisbas.q13"] %in% c(2,3)

# calculate sum scores and infrequency check for GAD7
survey_data$gad7             <- rowSums(survey_data[, c("gad7.q01", "gad7.q02", "gad7.q03", "gad7.q04", "gad7.q05", "gad7.q06", "gad7.q07")])
survey_data$gad7_infreq_pass <- survey_data[, "gad7.q08"] == 0

# calculate sum scores and infrequency check for GAD7
survey_data$pswq             <- rowSums(survey_data[, c("pswq.q01", "pswq.q02", "pswq.q03")])

# calculate sum scores and infrequency check for SHAPS
survey_data$shaps             <- rowSums(survey_data[, c("shaps.q01", "shaps.q02", "shaps.q03", "shaps.q04", "shaps.q05", "shaps.q06", "shaps.q07", "shaps.q08", "shaps.q09", "shaps.q10", "shaps.q11", "shaps.q12", "shaps.q13", "shaps.q14")])
survey_data$shaps_infreq_pass <- survey_data[, "shaps.q15"] %in% c(2,3)

# calculate how many checks were failed
survey_data$n_infreq_fail <- rowSums(!(survey_data[,c("susd_infreq_pass", "bisbas_infreq_pass", "gad7_infreq_pass", "shaps_infreq_pass")])) 
