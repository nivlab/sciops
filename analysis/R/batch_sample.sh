#! /usr/bin/env bash
#SBATCH -o /mnt/lustre/projects/qn57/dbennett/silver-screen/analysis/R/logs/silver-screen-%j.out
#SBATCH -t 1200
#SBATCH --mem 4000

echo "In the directory: `pwd` "
echo "As the user: `whoami` "
echo "on host: `hostname` "

# set up R
module load R/3.6.0-mkl

# set home directory
cd /mnt/lustre/projects/qn57/dbennett/silver-screen/analysis/R

# fit models
Rscript --vanilla fit_stan_cmd.R $1
