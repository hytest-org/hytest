#!/bin/bash
#SBATCH --mail-user=pnorton@usgs.gov
#SBATCH --mail-type=begin,end,fail
#SBATCH -J rechunk
#SBATCH -t 00:20:00
#SBATCH -o %j-rechunk.out
#SBATCH -p workq
#SBATCH -A wbeep
# #SBATCH --hint=nomultithread
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=40
# #SBATCH --array=0-2495%30

export PATH="$PATH:$HOME/anaconda3/bin"

source activate pangeo

base_dir=/caldera/projects/usgs/water/wbeep/conus404_work
wrf_dir=/caldera/hytest_scratch/scratch/forcing42year/tpBiasCorr
proc_vars_file=var_list.csv
target_store=/calscratch/scratch/conus404/pnorton_tmp2

python /caldera/projects/usgs/water/wbeep/conus404_work/conus404_rechunk_bias_corrected.py -i $SLURM_ARRAY_TASK_ID -b $base_dir -w $wrf_dir -v $proc_vars_file -d $target_store
