#### housekeeping ####
# dependencies
require(here)
require(ggplot2)

# read data and calculate sum scores
source(here("utilities", "source_data.R"))

# read metrics
metrics <- read.csv(here("..", "..", "data", "metrics.csv"))

# metrics <- subset(metrics, survey_data$platform == "mturk")
# survey_data <- subset(survey_data, survey_data$platform == "mturk")

bad_participants <- which(survey_data$n_infreq_fail > 0)
n_bad_participants <- sum(survey_data$n_infreq_fail > 0)
badness_order <- order(survey_data[, "n_infreq_fail"], decreasing=T)

counter <- 0


data <- cbind(survey_data$seven_down, metrics$RW_symm_beta)

n_reps <- 1000

rep_cor <- matrix(NA, nrow=n_bad_participants, ncol=n_reps)
prev_exclude <- NULL

for (n_fail in sort(unique(survey_data$n_infreq_fail[which(survey_data$n_infreq_fail > 0)]), decreasing=T)){
  

  # get relevant participant indices
  p_ix <- which(survey_data$n_infreq_fail >= n_fail)
  unique_ix <- which(survey_data$n_infreq_fail == n_fail)
  
  for (i in 1:length(unique_ix)){
    
    counter <- counter + 1
    
    for (j in 1:n_reps){
      if (length(unique_ix) == 1){
        remove_indices <- c(prev_exclude, unique_ix)
      } else{
        remove_indices <- c(prev_exclude, sample(unique_ix, i, replace=F))
      }
      d <- data[-remove_indices,]
      rep_cor[counter, j] <- cor.test(d[,1], d[,2], type="spearman", exact=F)$estimate
    }
  }
  
  prev_exclude <- c(prev_exclude, p_ix)
  
}
  

foo <- data.frame(t(apply(rep_cor, MARGIN=1, FUN=quantile, c(0.025,0.5,0.975))))
names(foo) <- c("lower", "median", "upper")

# flip order for plotting
foo <- foo[seq(from=dim(foo)[1], to=1, by=-1),]

# get critical values using normal approximation
foo$critical_values <- qnorm(0.025) / sqrt(seq(from=dim(data)[1] - n_bad_participants + 1, to=dim(data)[1],by=1) - 1) 
foo$n_included <- 1:n_bad_participants   



p <- ggplot(data=foo, aes(x=n_included)) + 
  geom_ribbon(aes(ymin=lower, ymax=upper), fill="grey70") +
  geom_line(aes(y=median), size=1.2) +
  geom_line(aes(y=critical_values), linetype="dashed", colour="#ff0a27", size=1.5) +
  geom_line(aes(y=-1*critical_values), linetype="dashed", colour="#ff0a27", size=1.5) +
  geom_hline(yintercept=0, size=1, linetype="dotted") +
  scale_y_continuous(limits=c(-0.5,0.5), breaks=c(-0.4, -0.2, 0, 0.2), expand=c(0,0), name="Spearman rho\n") +
  scale_x_continuous(limits=c(0, n_bad_participants * 1.05), breaks=c(0,n_bad_participants/4,n_bad_participants/2,3*n_bad_participants/4,n_bad_participants), labels=c(0,0.25,0.5,0.75,1), expand=c(0,0), name="\nProportion of bad participants included") +
  theme(panel.grid.major=element_blank(), 
        panel.grid.minor=element_blank(),
        panel.background=element_blank(),
        axis.title=element_text(size=24),
        axis.line=element_line(size=0.7),
        axis.text=element_text(size=20, colour="black")
  )
p

