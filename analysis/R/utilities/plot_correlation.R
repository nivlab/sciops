# dependencies
require(here)
require(ggplot2)

## correlations with a categorical cutoff (i.e., participants are treated as bad if they fail any infrequency checks)
plot_corr_categorical_cutoff <- function(survey_data, metrics, survey_var="seven_down", metric_var="RW_symm_beta", n_reps=1000, plot_title=""){
  
  # identify bad participants
  n_bad_participants <- sum(survey_data$n_infreq_fail > 0)
  bad_participants <- which(survey_data$n_infreq_fail > 0)
  
  # make dataframe with relevant variables
  data <- cbind(survey_data[, survey_var], metrics[, metric_var])
  
  # make container for estimated correlations
  rep_cor <- matrix(NA, nrow=n_bad_participants+1, ncol=n_reps)
  
  # loop over bad participants
  for (i in 0:n_bad_participants){
    
    # loop over repetitions (to permute which participants are excluded)
    for (rep in 1:n_reps){
      
      # remove relevant participants from overall dataframe
      if (i == n_bad_participants){
        d <- data
      } else {
        remove_indices <- sample(bad_participants, n_bad_participants-i, replace=F)
        d <- data[-remove_indices,]      
      }
      
      # calculate correlation for this subset of participants
      rep_cor[i+1, rep] <- cor.test(d[,1], d[,2], type="spearman", exact=F)$estimate
    }
  }
  
  # extract data for plotting
  plot_frame <- data.frame(t(apply(rep_cor, MARGIN=1, FUN=quantile, c(0.025,0.5,0.975))))
  names(plot_frame) <- c("lower", "median", "upper")
  
  # get critical values using normal approximation
  plot_frame$critical_values <- qnorm(0.025) / sqrt(seq(from=dim(data)[1] - n_bad_participants, to=dim(data)[1],by=1) - 1) 
  plot_frame$n_included <- 0:n_bad_participants
  
  # make plot
  p <- ggplot(data=plot_frame, aes(x=n_included)) + 
    geom_ribbon(aes(ymin=lower, ymax=upper), fill="grey70") +
    geom_line(aes(y=median), size=1.2) +
    geom_line(aes(y=critical_values), linetype="dashed", colour="#ff0a27", size=1.5) +
    geom_line(aes(y=-1*critical_values), linetype="dashed", colour="#ff0a27", size=1.5) +
    geom_hline(yintercept=0, size=1, linetype="dotted") +
    scale_y_continuous(limits=c(-0.7,0.7), breaks=c(-0.4, -0.2, 0, 0.2), expand=c(0,0), name="Spearman rho\n") +
    scale_x_continuous(limits=c(0, n_bad_participants * 1.05), breaks=c(0,n_bad_participants/4,n_bad_participants/2,3*n_bad_participants/4,n_bad_participants), labels=c(0,0.25,0.5,0.75,1), expand=c(0,0), name="\nProportion of bad participants included") +
    ggtitle(plot_title) + 
    theme(panel.grid.major=element_blank(), 
          panel.grid.minor=element_blank(),
          panel.background=element_blank(),
          plot.title=element_text(size=24, face="bold", hjust=0.5),
          axis.title=element_text(size=24),
          axis.line=element_line(size=0.7),
          axis.text=element_text(size=20, colour="black")
    )
  
  # return plot handle
  return(p)
  
} 


## correlations with an ordinal cutoff (i.e., participants with more infrequency check fails are excluded before participants with less)
plot_corr_ordinal_cutoff <- function(survey_data, metrics, survey_var="seven_down", metric_var="RW_symm_beta", n_reps=1000, plot_title=""){
  
  # identify bad participants
  n_bad_participants <- sum(survey_data$n_infreq_fail > 0)
  bad_participants <- which(survey_data$n_infreq_fail > 0)
  
  # make dataframe with relevant variables
  data <- cbind(survey_data[, survey_var], metrics[, metric_var])
  
  # make container for estimated correlations
  rep_cor <- matrix(NA, nrow=n_bad_participants, ncol=n_reps)
  prev_exclude <- NULL
  
  # make counter
  counter <- 0
  
  # iterate through number of infrequency checks failed from most to least
  for (n_fail in sort(unique(survey_data$n_infreq_fail[which(survey_data$n_infreq_fail > 0)]), decreasing=T)){
    
    # get relevant participant indices
    p_ix <- which(survey_data$n_infreq_fail >= n_fail)
    unique_ix <- which(survey_data$n_infreq_fail == n_fail)
    
    # loop over number of participants in this category
    for (i in 1:length(unique_ix)){
      
      # increment counter
      counter <- counter + 1
      
      # loop over repetitions (to permute which participants are excluded)
      for (j in 1:n_reps){
        
        if (length(unique_ix) == 1){
          remove_indices <- c(prev_exclude, unique_ix)
        } else{
          remove_indices <- c(prev_exclude, sample(unique_ix, i, replace=F))
        }
        
        # remove selected participants
        d <- data[-remove_indices,]
        
        # calculate correlation in reduced dataframe
        rep_cor[counter, j] <- cor.test(d[,1], d[,2], type="spearman", exact=F)$estimate
      }
    }
    
    # make sure participants with worse performance than the current check level are still excluded in future 
    prev_exclude <- c(prev_exclude, p_ix)
    
  }
  
  # make a dataframe for plotting
  plot_frame <- data.frame(t(apply(rep_cor, MARGIN=1, FUN=quantile, c(0.025,0.5,0.975))))
  names(plot_frame) <- c("lower", "median", "upper")
  
  # flip order for plotting
  plot_frame <- plot_frame[seq(from=dim(plot_frame)[1], to=1, by=-1),]
  
  # get critical values using normal approximation
  plot_frame$critical_values <- qnorm(0.025) / sqrt(seq(from=dim(data)[1] - n_bad_participants + 1, to=dim(data)[1],by=1) - 1) 
  plot_frame$n_included <- 1:n_bad_participants
  
  # make plot
  p <- ggplot(data=plot_frame, aes(x=n_included)) + 
    geom_ribbon(aes(ymin=lower, ymax=upper), fill="grey70") +
    geom_line(aes(y=median), size=1.2) +
    geom_line(aes(y=critical_values), linetype="dashed", colour="#ff0a27", size=1.5) +
    geom_line(aes(y=-1*critical_values), linetype="dashed", colour="#ff0a27", size=1.5) +
    geom_hline(yintercept=0, size=1, linetype="dotted") +
    scale_y_continuous(limits=c(-0.7,0.7), breaks=c(-0.4, -0.2, 0, 0.2), expand=c(0,0), name="Spearman rho\n") +
    scale_x_continuous(limits=c(0, n_bad_participants * 1.05), breaks=c(0,n_bad_participants/4,n_bad_participants/2,3*n_bad_participants/4,n_bad_participants), labels=c(0,0.25,0.5,0.75,1), expand=c(0,0), name="\nProportion of bad participants included") +
    ggtitle(plot_title) + 
    theme(panel.grid.major=element_blank(), 
          panel.grid.minor=element_blank(),
          panel.background=element_blank(),
          plot.title=element_text(size=24, face="bold", hjust=0.5),
          axis.title=element_text(size=24),
          axis.line=element_line(size=0.7),
          axis.text=element_text(size=20, colour="black")
    )
  
  # return plot handle
  return(p)
}
