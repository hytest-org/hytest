#!/bin/bash
############################################################################
# Parallelized slurm file: summarize hourly data into monthly files.
#                
# Usage: Call shell script using associated slurm file
#    e.g sbatch -o 
# Developed: 1/25/25, L. Staub
# Updated: 4/7/25, L. Staub
############################################################################

############################################################################

#SBATCH -p cpu  			  # set partition
#SBATCH -A impd 		  	  # set account
#SBATCH --job-name=ldasin_nco             # Job name
#SBATCH --nodes=1                         # Number of nodes (adjust as needed)
#SBATCH --ntasks=1                        # Number of tasks (one task per node/year)
#SBATCH --cpus-per-task=1                 # CPUs per task (adjust as needed)
#SBATCH --time=05:00:00                   # Time limit (adjust as needed)
#SBATCH --mail-type=ALL
#SBATCH --mail-user=	   	          # enter email
#SBATCH -o output_%A_%a.out	          # set path for job output files to be saved(A=main task a=subtask)
#SBATCH --array=2011-2013                 # set time step to process 

# Set the source directory containing year folders
SOURCE_DIR="/caldera/hovenweep/projects/usgs/water/impd/hytest/niwaa_wrfhydro_monthly_huc12_aggregations_sample_data/LDASIN"

# Load necessary modules 
module load nco

# Record the start time
global_start=$(date +%s)
echo "Job started at $(date)"

#Run the temporal aggregation 

srun /path/to/repo/hytest/dataset_processing/tutorials/niwaa_wrfhydro_monthly_huc12_agg/nco_process_ldasin.sh $SLURM_ARRAY_TASK_ID


# Record the end time
global_end=$(date +%s)
global_elapsed=$((global_end - global_start))
echo "Job finished at $(date)"
echo "Total job runtime: $global_elapsed seconds."



