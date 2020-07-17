#### housekeeping ####
# dependencies
require(here)
require(psych)
require(gridExtra)

tile_plot <- function(metrics, behav_measures, survey_data, survey_measures, include_ix, title=""){
  
  data_mat <- cbind(metrics[include_ix,behav_measures], survey_data[include_ix,survey_measures])
  colnames(data_mat) <- c(behav_names, survey_names)
  
  # calculate correlation matrix
  corr_mat <- corr.test(x = data_mat, # the input data
                        method = "spearman", # use non-parametric spearman correlations, since some of our variables are not normally distributed 
                        adjust = "none") # adjust p-values for multiple comparisons using a False Discovery Rate correction. Set to "none" for no correction
  
  mat_indices <- list(
    (length(behav_measures) + 1):dim(corr_mat$r)[2],
    1:length(behav_measures)
  )
  
  plot_ix <- ggplot(melt(corr_mat$r[mat_indices[[1]], mat_indices[[2]]]), aes(Var1, Var2, fill=value)) + 
              geom_tile(height=0.95, width=0.95) +
              scale_fill_gradient2(low="blue", mid="white", high="#ff0a27", lim=c(-0.6,0.6)) +
              theme_minimal() +
              coord_equal() +
              labs(x="",y="",fill="Corr") +
              ggtitle(title) +
              theme(axis.text.x=element_text(size=13, angle=45, vjust=1, hjust=1, 
                                             margin=margin(-3,0,0,0)),
                    axis.text.y=element_text(size=13, margin=margin(0,-3,0,0)),
                    plot.title = element_text(size=20, face="bold", hjust=0.5),
                    panel.grid.major=element_blank()) + 
              geom_point(shape=4, aes(size=ifelse(melt(corr_mat$p[mat_indices[[1]], mat_indices[[2]]])[,3] < .05, "significant", "non_significant"))) +
              scale_size_manual(values=c(significant=NA, non_significant=4), guide="none")
  
  return(plot_ix)
}

# read data and calculate sum scores
source(here("utilities", "source_data.R"))

# reorder shaps so it is a measure of anhedonia
survey_data$shaps <- -survey_data$shaps

# read metrics
metrics <- read.csv(here("..", "..", "data", "metrics.csv"))

# set screening criterion
include_ix <- survey_data$platform %in% c("prolific", "mturk")

# first pass: correlations with different measures with/without screening
survey_measures <- c("seven_down", "seven_up", "bas_rwd", "bas_drive", "bis", "gad7", "pswq", "shaps")
survey_names <- c("Depression (7-up)", "Hypomania (7-down)", "BAS reward sensitivity", "BAS drive", "BIS", "State anxiety (GAD-7)", "Trait Anxiety (PSWQ)", "Anhedonia (SHAPS, reverse-scored)")
behav_measures <- c("prop_correct", "WSLS_ratio", "RW_symm_beta", "RW_symm_eta")
behav_names <- c("Proportion correct", "WSLS ratio", "Softmax beta", "Learning rate") 

# plot correlations under different inclusion criteria
all_plot <- tile_plot(title="All participants\n", metrics, behav_measures, survey_data, survey_measures, include_ix=survey_data$n_infreq_fail >= 0)
include_plot <- tile_plot(title="Participants included with any-fail criterion\n", metrics, behav_measures, survey_data, survey_measures, include_ix=survey_data$n_infreq_fail == 0)
exclude_plot <- tile_plot(title="Participants excluded with any-fail criterion\n", metrics, behav_measures, survey_data, survey_measures, include_ix=survey_data$n_infreq_fail > 0)

all_plot
include_plot
exclude_plot
